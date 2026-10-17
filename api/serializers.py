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
    test_copy = serializers.SerializerMethodField()

    class Meta:
        model = SubjectMark
        fields = ['id', 'student', 'subject_name', 'max_marks', 'obtained_marks', 'status', 'test_copy', 'test_copy_name']

    def get_test_copy(self, obj):
        if obj.test_copy:
            try:
                # Agar test_copy ke paas .url attribute hai (Cloudinary / FileField)
                if hasattr(obj.test_copy, 'url'):
                    return str(obj.test_copy.url)
                # Agar wo pehle se hi string URL hai
                url_str = str(obj.test_copy)
                if url_str.startswith('http'):
                    return url_str
            except Exception:
                pass
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        uploaded_files = request.FILES.getlist('test_copy') if request else []
        
        single_file = validated_data.pop('test_copy', None)
        if not uploaded_files and single_file:
            uploaded_files = [single_file]

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
                        pdf_filename = f"{base_name}_combined_copy.pdf"
                        
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

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        uploaded_files = request.FILES.getlist('test_copy') if request else []
        single_file = validated_data.pop('test_copy', None)
        if not uploaded_files and single_file:
            uploaded_files = [single_file]

        if uploaded_files:
            try:
                if len(uploaded_files) == 1 and getattr(uploaded_files[0], 'name', '').lower().endswith('.pdf'):
                    f = uploaded_files[0]
                    instance.test_copy = f
                    instance.test_copy_name = getattr(f, 'name', 'document.pdf')
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
                        images[0].save(pdf_io, format='PDF', save_all=True, append_images=images[1:])
                        pdf_filename = f"{base_name}_combined_copy.pdf"
                        
                        instance.test_copy = SimpleUploadedFile(
                            pdf_filename, 
                            pdf_io.getvalue(), 
                            content_type='application/pdf'
                        )
                        instance.test_copy_name = pdf_filename
                    elif single_file:
                        instance.test_copy = single_file
                        instance.test_copy_name = getattr(single_file, 'name', 'document.pdf')
            except Exception as e:
                if single_file:
                    instance.test_copy = single_file
                    instance.test_copy_name = getattr(single_file, 'name', 'document.pdf')

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