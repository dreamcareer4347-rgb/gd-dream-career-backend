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
    test_copy = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = SubjectMark
        fields = ['id', 'student', 'subject_name', 'max_marks', 'obtained_marks', 'status', 'test_copy', 'test_copy_name']

    def create(self, validated_data):
        file_obj = validated_data.pop('test_copy', None)
        if file_obj:
            file_name = getattr(file_obj, 'name', 'document.jpg')
            
            # Agar upload ki gayi file image hai, toh use automatically PDF me convert kar do
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                try:
                    image = Image.open(file_obj)
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    
                    pdf_io = io.BytesIO()
                    image.save(pdf_io, format='PDF')
                    validated_data['test_copy'] = pdf_io.getvalue()
                    
                    # File ka naam automatically .pdf me badal do
                    base_name = file_name.rsplit('.', 1)[0]
                    validated_data['test_copy_name'] = f"{base_name}_test_copy.pdf"
                except Exception as e:
                    # Agar conversion me koi issue aaye toh fallback format me save ho jaye
                    validated_data['test_copy'] = file_obj.read()
                    validated_data['test_copy_name'] = file_name
            else:
                # Agar pehle se hi PDF hai toh waise hi save kar lo
                validated_data['test_copy'] = file_obj.read()
                validated_data['test_copy_name'] = file_name
                
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file_obj = validated_data.pop('test_copy', None)
        if file_obj:
            file_name = getattr(file_obj, 'name', 'document.jpg')
            
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                try:
                    image = Image.open(file_obj)
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    
                    pdf_io = io.BytesIO()
                    image.save(pdf_io, format='PDF')
                    instance.test_copy = pdf_io.getvalue()
                    
                    base_name = file_name.rsplit('.', 1)[0]
                    instance.test_copy_name = f"{base_name}_test_copy.pdf"
                except Exception as e:
                    instance.test_copy = file_obj.read()
                    instance.test_copy_name = file_name
            else:
                instance.test_copy = file_obj.read()
                instance.test_copy_name = file_name
                
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