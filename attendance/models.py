from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ("STUDENT", 'Student'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

class Course(models.Model):
    title = models.CharField(max_length=100, unique=True)

    teachers = models.ManyToManyField(
        'CustomUser',
        limit_choices_to={'role': 'TEACHER'},
        related_name='course_taught'
    )

    def __str__(self):
        return self.title
    
class Student(models.Model):
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        limit_choices_to={'role': 'STUDENT'}
    )

    full_name = models.CharField(max_length=100)

    courses = models.ManyToManyField(Course, related_name='students')

    def __str__(self):
        return self.full_name
    
class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title} on {self.date} ({self.status})"