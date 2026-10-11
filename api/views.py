# File path: backend/api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Student, ContactInquiry, FeePayment, SubjectMark
from .serializers import (
    StudentSerializer, 
    ContactInquirySerializer, 
    FeePaymentSerializer, 
    SubjectMarkSerializer
)

@api_view(['POST'])
def get_student_performance(request):
    roll_no = request.data.get('roll_number')
    pin = request.data.get('result_pin')

    try:
        student = Student.objects.get(roll_number=roll_no, result_pin=pin)
        serializer = StudentSerializer(student)
        return Response({"success": True, "data": serializer.data})
    except Student.DoesNotExist:
        return Response({"success": False, "message": "Invalid Roll Number or PIN"}, status=400)

@api_view(['POST'])
def submit_inquiry(request):
    serializer = ContactInquirySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": True, "message": "Inquiry submitted successfully!"})
    return Response({"success": False, "errors": serializer.errors}, status=400)


# --- Admin ViewSets for Full Control (Add, Edit, Delete Students & Records) ---
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer

class SubjectMarkViewSet(viewsets.ModelViewSet):
    queryset = SubjectMark.objects.all()
    serializer_class = SubjectMarkSerializer

class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all().order_by('-created_at')
    serializer_class = ContactInquirySerializer