from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import CustomUser, Course, Student, AttendanceRecord

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(AttendanceRecord)