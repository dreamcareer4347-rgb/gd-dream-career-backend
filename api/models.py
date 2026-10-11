# File path: backend/api/models.py
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    parents_name = models.CharField(max_length=100, default="Shri Guardian")
    roll_number = models.CharField(max_length=50, unique=True)
    result_pin = models.CharField(max_length=4)
    student_class = models.CharField(max_length=50)
    attendance = models.CharField(max_length=10, default="95%")
    grade = models.CharField(max_length=5, default="A+")
    total_percentage = models.CharField(max_length=10, default="88%")
    student_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    
    # Specific Performance Pillars
    english_speaking_score = models.CharField(max_length=20, default="88% (Fluent)")
    deep_learning_score = models.CharField(max_length=20, default="90% (Advanced)")
    written_performance_score = models.CharField(max_length=20, default="85% (Good)")
    math_improvement_score = models.CharField(max_length=20, default="92% (Excellent)")
    
    # Overall Fee Summary
    total_fee = models.IntegerField(default=12000)
    paid_fee = models.IntegerField(default=10000)
    due_fee = models.IntegerField(default=2000)
    fee_status = models.CharField(max_length=20, default="Partial Paid")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

# --- Naya Model: Monthly Fee Transaction History ---
class FeePayment(models.Model):
    student = models.ForeignKey(Student, related_name='fee_history', on_delete=models.CASCADE)
    month_name = models.CharField(max_length=50) # e.g. "January 2026"
    amount_paid = models.IntegerField()
    payment_date = models.DateField()
    payment_mode = models.CharField(max_length=50, default="Cash") # Cash / UPI / Online
    receipt_note = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.student.name} - {self.month_name} (₹{self.amount_paid})"

class SubjectMark(models.Model):
    student = models.ForeignKey(Student, related_name='subjects', on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    max_marks = models.IntegerField(default=100)
    obtained_marks = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="Pass")
    test_copy = models.FileField(upload_to='test_copies/', blank=True, null=True)

    def __str__(self):
        return f"{self.subject_name} - {self.student.name}"

class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    student_class = models.CharField(max_length=50)
    interested_course = models.CharField(max_length=100)
    inquiry_type = models.CharField(max_length=50)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.name} ({self.mobile})"