# File path: backend/api/serializers.py
from rest_framework import serializers
from .models import Student, SubjectMark, ContactInquiry, FeePayment

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'month_name', 'amount_paid', 'payment_date', 'payment_mode', 'receipt_note']

class SubjectMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectMark
        fields = ['id', 'student', 'subject_name', 'max_marks', 'obtained_marks', 'status']

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