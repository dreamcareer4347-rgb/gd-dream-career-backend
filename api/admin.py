# File path: backend/api/admin.py
from django.contrib import admin
from .models import Student, SubjectMark, ContactInquiry, FeePayment

class SubjectMarkInline(admin.TabularInline):
    model = SubjectMark
    extra = 1

class FeePaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 1

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'student_class', 'total_fee', 'paid_fee', 'due_fee', 'fee_status')
    search_fields = ('name', 'roll_number', 'parents_name')
    inlines = [FeePaymentInline, SubjectMarkInline]

admin.site.register(Student, StudentAdmin)
admin.site.register(SubjectMark)
admin.site.register(FeePayment)
admin.site.register(ContactInquiry)