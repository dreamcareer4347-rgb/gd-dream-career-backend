# File path: backend/api/views.py
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
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


# --- Admin ViewSets for Full Control ---
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print("DB SAVE ERROR:", str(e))
                return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        print("SERIALIZER ERRORS:", serializer.errors)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer

class SubjectMarkViewSet(viewsets.ModelViewSet):
    queryset = SubjectMark.objects.all()
    serializer_class = SubjectMarkSerializer
    parser_classes = (MultiPartParser, FormParser)

    # Naya action jo database se binary file fetch karke view/download karayega
    @action(detail=True, methods=['get'])
    def download_file(self, request, pk=None):
        instance = self.get_object()
        if not instance.test_copy:
            return HttpResponse("File not found in database", status=404)
        
        file_data = bytes(instance.test_copy)
        file_name = instance.test_copy_name or "document.pdf"
        
        content_type = "application/pdf"
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            content_type = "image/jpeg"
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response

class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all().order_by('-created_at')
    serializer_class = ContactInquirySerializer