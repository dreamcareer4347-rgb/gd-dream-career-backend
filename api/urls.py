# File path: backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    get_student_performance, 
    submit_inquiry, 
    StudentViewSet, 
    FeePaymentViewSet, 
    SubjectMarkViewSet, 
    ContactInquiryViewSet,
    verify_admin_login
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'fee-payments', FeePaymentViewSet)
router.register(r'subject-marks', SubjectMarkViewSet)
router.register(r'inquiries-list', ContactInquiryViewSet)

urlpatterns = [
    # Purane custom endpoints
    path('performance/', get_student_performance, name='student_performance'),
    path('inquiry/', submit_inquiry, name='submit_inquiry'),
    
    # Naye automated CRUD endpoints (admin panel ke liye)
    path('', include(router.urls)),
    path('admin-login/', verify_admin_login, name='admin-login'),
]