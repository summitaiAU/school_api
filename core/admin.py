from django.contrib import admin
from .models import School, SchoolClass, Student

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'grade_level', 'academic_year')
    list_filter = ('school', 'grade_level', 'academic_year')
    search_fields = ('name', 'school__name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'school', 'school_class')
    list_filter = ('school', 'school_class')
    search_fields = ('first_name', 'last_name', 'student_id', 'email', 'parent_name')