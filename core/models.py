from django.db import models

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    grade_level = models.CharField(max_length=50, blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    class Meta:
        verbose_name_plural = "School Classes"

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='students')
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    parent_name = models.CharField(max_length=200, blank=True, null=True)
    parent_contact = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"