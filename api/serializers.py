# File path: backend/api/serializers.py
from rest_framework import serializers
from PIL import Image
import io
from .models import Student, SubjectMark, ContactInquiry, FeePayment

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'month_name', 'amount_paid', 'payment_date', 'payment_mode', 'receipt_note']

class SubjectMarkSerializer(serializers.ModelSerializer):
    # Multiple files support ke liye list field ya handle karna
    test_copy = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = SubjectMark
        fields = ['id', 'student', 'subject_name', 'max_marks', 'obtained_marks', 'status', 'test_copy', 'test_copy_name']

    def create(self, validated_data):
        # Request se saari uploaded files nikalne ke liye
        request = self.context.get('request')
        uploaded_files = request.FILES.getlist('test_copy') if request else []
        
        # Agar request context se na mile toh validated_data se single file lo
        single_file = validated_data.pop('test_copy', None)
        if not uploaded_files and single_file:
            uploaded_files = [single_file]

        if uploaded_files:
            try:
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
                    elif fname.lower().endswith('.pdf'):
                        # Agar user ne PDF upload kiya hai toh usko waise hi handle kar lo (ya first file rakho)
                        validated_data['test_copy'] = f.read()
                        validated_data['test_copy_name'] = fname
                        return super().create(validated_data)

                if images:
                    # Agar multiple images hain, toh sabko ek single PDF me combine kar do
                    pdf_io = io.BytesIO()
                    images[0].save(
                        pdf_io, 
                        format='PDF', 
                        save_all=True, 
                        append_images=images[1:]
                    )
                    validated_data['test_copy'] = pdf_io.getvalue()
                    validated_data['test_copy_name'] = f"{base_name}_combined_copy.pdf"
                else:
                    if single_file:
                        validated_data['test_copy'] = single_file.read()
                        validated_data['test_copy_name'] = getattr(single_file, 'name', 'document.pdf')
            except Exception as e:
                if single_file:
                    validated_data['test_copy'] = single_file.read()
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
                    elif fname.lower().endswith('.pdf'):
                        instance.test_copy = f.read()
                        instance.test_copy_name = fname
                        return super().update(instance, validated_data)

                if images:
                    pdf_io = io.BytesIO()
                    images[0].save(pdf_io, format='PDF', save_all=True, append_images=images[1:])
                    instance.test_copy = pdf_io.getvalue()
                    instance.test_copy_name = f"{base_name}_combined_copy.pdf"
                else:
                    if single_file:
                        instance.test_copy = single_file.read()
                        instance.test_copy_name = getattr(single_file, 'name', 'document.pdf')
            except Exception as e:
                if single_file:
                    instance.test_copy = single_file.read()
                    instance.test_copy_name = getattr(single_file, 'name', 'document.pdf')

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.test_copy:
            representation['test_copy'] = f"/api/subject-marks/{instance.id}/download_file/"
        else:
            representation['test_copy'] = None
        return representation

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