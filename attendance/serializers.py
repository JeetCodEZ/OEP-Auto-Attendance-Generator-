from rest_framework import serializers
from .models import CustomUser, Student, Course, AttendanceRecord
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = ['id', 'username', 'role']

class CourseSerializer(serializers.ModelSerializer):
    teacher_names = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'teachers',
            'teacher_names'
        ]

    def get_teacher_names(self, obj):
        return [teacher.username for teacher in obj.teachers.all()]

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student

        fields = [
            'user',
            'username',
            'full_name',
            'courses'
        ]
    
class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = AttendanceRecord

        fields = [
            'id',
            'student',
            'student_name',
            'course',
            'course_title',
            'date',
            'status'
        ]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['role'] = user.role
        
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            role = validated_data.get('role', 'STUDENT')
        )

        return user