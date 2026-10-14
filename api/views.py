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

    if not roll_no or not pin:
        return Response({"success": False, "message": "Roll Number aur Result PIN enter karna anivarya hai."}, status=200)

    try:
        student = Student.objects.get(roll_number=roll_no.strip(), result_pin=pin.strip())
        subjects = student.subjects.all()
        
        def get_skill_avg(keywords):
            matched = [s for s in subjects if any(kw in s.subject_name.lower() for kw in keywords)]
            if not matched:
                return None
            total_obtained = sum(s.obtained_marks for s in matched)
            total_max = sum(s.max_marks for s in matched)
            if total_max == 0:
                return None
            return round((total_obtained / total_max) * 100)

        # Calculate dynamic scores based on selected dropdown subject names
        eng_speaking_pct = get_skill_avg(['english speaking'])
        deep_eng_pct = get_skill_avg(['deep english learning'])
        written_pct = get_skill_avg(['written performance'])
        math_pct = get_skill_avg(['math improvement'])

        # Serialize student data
        serializer = StudentSerializer(student)
        data = dict(serializer.data)

        # Force override: Agar marks hain toh calculate karo, nahi toh "Not Uploaded Yet" dikhao
        if eng_speaking_pct is not None:
            status_text = "Fluent" if eng_speaking_pct >= 80 else ("Good" if eng_speaking_pct >= 60 else "Improving")
            data['english_speaking_score'] = f"{eng_speaking_pct}% ({status_text})"
        else:
            data['english_speaking_score'] = "Not Uploaded Yet"
            
        if deep_eng_pct is not None:
            status_text = "Advanced" if deep_eng_pct >= 80 else ("Intermediate" if deep_eng_pct >= 60 else "Basic")
            data['deep_learning_score'] = f"{deep_eng_pct}% ({status_text})"
        else:
            data['deep_learning_score'] = "Not Uploaded Yet"
            
        if written_pct is not None:
            status_text = "Good" if written_pct >= 80 else ("Steady" if written_pct >= 60 else "Needs Practice")
            data['written_performance_score'] = f"{written_pct}% ({status_text})"
        else:
            data['written_performance_score'] = "Not Uploaded Yet"
            
        if math_pct is not None:
            status_text = "Excellent" if math_pct >= 80 else ("Growing" if math_pct >= 60 else "Average")
            data['math_improvement_score'] = f"{math_pct}% ({status_text})"
        else:
            data['math_improvement_score'] = "Not Uploaded Yet"

        return Response({"success": True, "data": data}, status=200)
        
    except Student.DoesNotExist:
        return Response({"success": False, "message": "Galat Roll Number ya Result PIN! Kripya sahi detail dalein."}, status=200)

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