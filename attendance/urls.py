from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . views import (
    CustomUserViewSet,
    CourseViewSet,
    StudentViewSet,
    AttendanceRecordViewSet,
    UserMeView,
    AttendanceUploadView,
    TeacherListView
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'students', StudentViewSet)
router.register(r'records', AttendanceRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserMeView.as_view(), name = 'user-me'),
    path('upload/', AttendanceUploadView.as_view(), name='attendance-upload'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
]