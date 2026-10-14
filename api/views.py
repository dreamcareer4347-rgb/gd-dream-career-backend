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
        
        # --- Dynamic Performance Calculation from Test Marks / Subjects ---
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

        # Calculate dynamic scores based on subject name keywords
        eng_speaking_pct = get_skill_avg(['speaking', 'english speaking', 'convers'])
        deep_eng_pct = get_skill_avg(['deep', 'grammar', 'literature', 'deep english', 'deep learning'])
        written_pct = get_skill_avg(['written', 'writing', 'essay', 'spelling'])
        math_pct = get_skill_avg(['math', 'mathematics', 'calculation', 'arithmetic'])

        # Serialize student data
        serializer = StudentSerializer(student)
        data = dict(serializer.data)

        # Override default score strings with dynamic calculated values if test records exist
        if eng_speaking_pct is not None:
            data['english_speaking_score'] = f"{eng_speaking_pct}% (Fluent)" if eng_speaking_pct >= 75 else f"{eng_speaking_pct}% (Good)"
        if deep_eng_pct is not None:
            data['deep_learning_score'] = f"{deep_eng_pct}% (Advanced)" if deep_eng_pct >= 75 else f"{deep_eng_pct}% (Improving)"
        if written_pct is not None:
            data['written_performance_score'] = f"{written_pct}% (Good)" if written_pct >= 75 else f"{written_pct}% (Steady)"
        if math_pct is not None:
            data['math_improvement_score'] = f"{math_pct}% (Excellent)" if math_pct >= 75 else f"{math_pct}% (Growing)"

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

    # Action to fetch binary file stored inside Neon PostgreSQL database
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