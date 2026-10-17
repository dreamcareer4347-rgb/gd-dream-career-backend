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
    total_percentage = models.CharField(max_length=10, default="Pending")
    student_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    
    # Specific Performance Pillars Defaults
    english_speaking_score = models.CharField(max_length=50, default="Not Uploaded Yet")
    deep_learning_score = models.CharField(max_length=50, default="Not Uploaded Yet")
    written_performance_score = models.CharField(max_length=50, default="Not Uploaded Yet")
    math_improvement_score = models.CharField(max_length=50, default="Not Uploaded Yet")
    
    # Overall Fee Summary
    total_fee = models.IntegerField(default=1000)
    paid_fee = models.IntegerField(default=0)
    due_fee = models.IntegerField(default=1000)
    fee_status = models.CharField(max_length=20, default="Due Pending")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

# --- Admin Database Authentication Model ---
class AdminCredential(models.Model):
    username = models.CharField(max_length=50, unique=True)
    secret_pin = models.CharField(max_length=20)

    def __str__(self):
        return f"Admin: {self.username}"

# --- Monthly Fee Transaction History ---
class FeePayment(models.Model):
    student = models.ForeignKey(Student, related_name='fee_history', on_delete=models.CASCADE)
    month_name = models.CharField(max_length=50)
    amount_paid = models.IntegerField()
    payment_date = models.DateField()
    payment_mode = models.CharField(max_length=50, default="Cash")
    receipt_note = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.student.name} - {self.month_name} (₹{self.amount_paid})"

class SubjectMark(models.Model):
    student = models.ForeignKey(Student, related_name='subjects', on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    max_marks = models.IntegerField(default=100)
    obtained_marks = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="Pass")
    
    # OPTIMIZED FOR FREE TIER: Cloudinary storage link instead of heavy DB Binary bytes
    test_copy = models.FileField(upload_to='test_copies/', blank=True, null=True)
    test_copy_name = models.CharField(max_length=255, blank=True, null=True)

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