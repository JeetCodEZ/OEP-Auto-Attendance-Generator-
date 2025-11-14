from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import CustomUser, Course, Student, AttendanceRecord
from .serializers import (
    CustomUserSerializer,
    CourseSerializer,
    StudentSerializer,
    AttendanceRecordSerializer,
    UserCreateSerializer
)
from .permissions import IsAdminUser, IsTeacherAndOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import pandas as pd

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        
        return CustomUserSerializer

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()
        if user.role == 'ADMIN':
            return Course.objects.all()
        if user.role == 'TEACHER':
            return Course.objects.filter(teachers=user)
        if user.role == 'STUDENT':
            try:
                return user.student.courses.all()
            except Student.DoesNotExist:
                return Course.objects.none()
        return Course.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser]

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            queryset = AttendanceRecord.objects.none()
        elif user.role == 'ADMIN':
            queryset = AttendanceRecord.objects.all()
        elif user.role == 'TEACHER':
            queryset = AttendanceRecord.objects.filter(course__teachers=user)
        elif user.role == 'STUDENT':
            queryset = AttendanceRecord.objects.filter(student__user=user)
        else:
            queryset = AttendanceRecord.objects.none()

        course_id = self.request.query_params.get('course_id')
        date = self.request.query_params.get('date')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset.order_by('-date')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['create','update', 'partial_update']:
            return [permissions.IsAuthenticated(), (IsAdminUser | IsTeacherAndOwner)()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data)

class AttendanceUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')
        date = request.query_params.get('date')

        if not course_id or not date:
            return Response(
                {'error': 'Missing course_id or date query parameters'},
                status = status.HTTP_400_BAD_REQUEST
            )
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if 'file' not in request.data:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        file_obj = request.data['file']

        try:
            df = pd.read_excel(file_obj)
            df.columns = df.columns.str.lower()
            if 'name' not in df.columns or 'status' not in df.columns:
                return Response(
                    {'error': 'Excel file must have "Name" and "Status" columns'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to read Excel file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        updated_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                student_name = row['name']
                attendance_status = str(row['status']).capitalize()

                student = Student.objects.get(full_name__iexact=student_name)
                
                record, created = AttendanceRecord.objects.update_or_create(
                    student = student,
                    course = course,
                    date = date,
                    defaults = {'status': attendance_status}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Student.DoesNotExist:
                errors.append(f'Student not found: {student_name}')
                continue
            except Exception as e:
                errors.append(f'Error processing row {index+1} ({student_name}): {str(e)}')
                continue

        return Response(
            {
                'message': 'Upload successful',
                'records_created': created_count,
                'records_updated': updated_count,
                'errors': errors
            },
            status = status.HTTP_201_CREATED
        )

class TeacherListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        teachers = CustomUser.objects.filter(role='TEACHER')

        serializer = CustomUserSerializer(teachers, many=True)
        return Response(serializer.data)
    