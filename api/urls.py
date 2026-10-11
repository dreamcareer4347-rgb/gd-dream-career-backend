from django.urls import path
from .views import get_student_performance, submit_inquiry

urlpatterns = [
    path('performance/', get_student_performance, name='student_performance'),
    path('inquiry/', submit_inquiry, name='submit_inquiry'),
]