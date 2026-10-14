# File path: backend/api/admin.py
from django.contrib import admin
from .models import Student, SubjectMark, FeePayment, ContactInquiry

class SubjectMarkInline(admin.TabularInline):
    model = SubjectMark
    extra = 1

class FeePaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 1

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'student_class', 'total_fee', 'grade', 'created_at')
    search_fields = ('name', 'roll_number', 'parents_name')
    list_filter = ('student_class', 'grade')
    inlines = [SubjectMarkInline, FeePaymentInline]

@admin.register(SubjectMark)
class SubjectMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_name', 'max_marks', 'obtained_marks', 'status')
    list_filter = ('subject_name', 'status')

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'month_name', 'amount_paid', 'payment_date', 'payment_mode')
    list_filter = ('payment_mode', 'month_name')

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'student_class', 'interested_course', 'created_at')
    search_fields = ('name', 'mobile')