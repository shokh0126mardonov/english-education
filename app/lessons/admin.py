from django.contrib import admin
from .models import Course, Group, Enrollment, Lesson, Attendance, Material

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'created_at']
    search_fields = ['name']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'teacher', 'status', 'created_at']
    list_filter = ['status', 'course', 'teacher']
    search_fields = ['name']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'status', 'joined_date']
    list_filter = ['status', 'group']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['topic', 'group', 'date', 'start_time', 'end_time']
    list_filter = ['group', 'date']
    search_fields = ['topic']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'status']
    list_filter = ['status', 'lesson__group', 'lesson__date']
    search_fields = ['student__username']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'type']
    list_filter = ['type', 'course']
    search_fields = ['title']
