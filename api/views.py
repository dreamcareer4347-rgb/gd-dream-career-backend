from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student, ContactInquiry
from .serializers import StudentSerializer, ContactInquirySerializer

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