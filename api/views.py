# File path: backend/api/views.py
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Student, ContactInquiry, FeePayment, SubjectMark, AdminCredential
from .serializers import (
    StudentSerializer, 
    ContactInquirySerializer, 
    FeePaymentSerializer, 
    SubjectMarkSerializer
)

@api_view(['POST'])
def verify_admin_login(request):
    username = request.data.get('username')
    pin = request.data.get('secret_pin')

    if not username or not pin:
        return Response({"success": False, "message": "Username aur Secret PIN enter karna anivarya hai."}, status=200)

    try:
        admin = AdminCredential.objects.get(username=username.strip(), secret_pin=pin.strip())
        return Response({"success": True, "message": "Login successful!"}, status=200)
    except AdminCredential.DoesNotExist:
        return Response({"success": False, "message": "Galat Username ya Secret PIN! Kripya sahi detail dalein."}, status=200)

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

        eng_speaking_pct = get_skill_avg(['english speaking'])
        deep_eng_pct = get_skill_avg(['deep english learning'])
        written_pct = get_skill_avg(['written performance'])
        math_pct = get_skill_avg(['math improvement'])

        serializer = StudentSerializer(student, context={'request': request})
        data = dict(serializer.data)

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
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)

class SubjectMarkViewSet(viewsets.ModelViewSet):
    queryset = SubjectMark.objects.all()
    serializer_class = SubjectMarkSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)  # <-- JSONParser added here to fix 415 error

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all().order_by('-created_at')
    serializer_class = ContactInquirySerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)