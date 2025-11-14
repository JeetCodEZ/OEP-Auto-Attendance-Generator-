from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
    
class IsTeacherAndOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and request.user.role == 'TEACHER'):
            return False
        
        return request.user in obj.course.teachers.all()