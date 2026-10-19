# File path: backend/api/serializers.py
from rest_framework import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from .models import Student, SubjectMark, ContactInquiry, FeePayment

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'month_name', 'amount_paid', 'payment_date', 'payment_mode', 'receipt_note']

class SubjectMarkSerializer(serializers.ModelSerializer):
    test_copy = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = SubjectMark
        fields = ['id', 'student', 'subject_name', 'max_marks', 'obtained_marks', 'status', 'test_copy', 'test_copy_name']

    def to_representation(self, instance):
        """Ensures that when fetching data, test_copy returns the clean Cloudinary URL with correct raw/image resource type"""
        representation = super().to_representation(instance)
        if instance.test_copy:
            try:
                if hasattr(instance.test_copy, 'url'):
                    url = str(instance.test_copy.url)
                else:
                    url = str(instance.test_copy)
                
                # Fix redundant /media/ segment in Cloudinary URLs
                if 'res.cloudinary.com' in url:
                    if '/upload/' in url and '/media/' in url:
                        parts = url.split('/upload/')
                        if len(parts) == 2:
                            sub_path = parts[1]
                            if '/media/' in sub_path:
                                sub_path = sub_path.replace('/media/', '/')
                            url = f"{parts[0]}/upload/{sub_path}"
                    
                    # PDFs aur combined files ke liye Cloudinary 'raw/upload' use karta hai
                    is_pdf_or_doc = '_combined' in url or str(getattr(instance, 'test_copy_name', '')).lower().endswith('.pdf')
                    if is_pdf_or_doc and '/image/upload/' in url:
                        url = url.replace('/image/upload/', '/raw/upload/')
                
                # Clean up any hex/unicode encoding or double backslashes in URL paths
                if '%5C' in url or '\\' in url:
                    url = url.replace('%5C', '').replace('\\', '')
                
                representation['test_copy'] = url
            except Exception:
                representation['test_copy'] = None
        else:
            representation['test_copy'] = None
        return representation

    def _process_uploaded_files(self, request, validated_data, instance=None):
        uploaded_files = request.FILES.getlist('test_copy') if (request and hasattr(request, 'FILES')) else []
        single_file = validated_data.pop('test_copy', None)

        if not uploaded_files and single_file:
            uploaded_files = [single_file]

        if not uploaded_files:
            if instance and hasattr(instance, 'test_copy'):
                validated_data['test_copy'] = instance.test_copy
            return validated_data

        if uploaded_files:
            try:
                if len(uploaded_files) == 1 and getattr(uploaded_files[0], 'name', '').lower().endswith('.pdf'):
                    f = uploaded_files[0]
                    validated_data['test_copy'] = f
                    validated_data['test_copy_name'] = getattr(f, 'name', 'document.pdf')
                else:
                    images = []
                    base_name = "test_copy"
                    
                    for f in uploaded_files:
                        fname = getattr(f, 'name', 'doc.jpg')
                        base_name = fname.rsplit('.', 1)[0]
                        
                        if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                            img = Image.open(f)
                            if img.mode == 'RGBA':
                                img = img.convert('RGB')
                            images.append(img)

                    if images:
                        pdf_io = io.BytesIO()
                        images[0].save(
                            pdf_io, 
                            format='PDF', 
                            save_all=True, 
                            append_images=images[1:]
                        )
                        pdf_filename = f"{base_name}_combined.pdf"
                        
                        validated_data['test_copy'] = SimpleUploadedFile(
                            pdf_filename, 
                            pdf_io.getvalue(), 
                            content_type='application/pdf'
                        )
                        validated_data['test_copy_name'] = pdf_filename
                    elif single_file:
                        validated_data['test_copy'] = single_file
                        validated_data['test_copy_name'] = getattr(single_file, 'name', 'document.pdf')
            except Exception as e:
                if single_file:
                    validated_data['test_copy'] = single_file
                    validated_data['test_copy_name'] = getattr(single_file, 'name', 'document.pdf')
        
        return validated_data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data = self._process_uploaded_files(request, validated_data, instance=None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        validated_data = self._process_uploaded_files(request, validated_data, instance=instance)
        return super().update(instance, validated_data)

class StudentSerializer(serializers.ModelSerializer):
    subjects = SubjectMarkSerializer(many=True, read_only=True)
    fee_history = FeePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = '__all__'