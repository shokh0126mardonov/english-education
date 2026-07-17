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

from django import forms
import os
import tempfile
import threading
from django.utils import timezone
from django.contrib import messages
from app.common.services.youtube import YouTubeService
from app.common.services.exceptions import YouTubeError

class LessonAdminForm(forms.ModelForm):
    video_file = forms.FileField(
        required=False, 
        label="Video yuklash (YouTube)", 
        help_text="Bu yerda yuklangan video avtomatik tarzda YouTube kanalga yuklanadi."
    )

    class Meta:
        model = Lesson
        fields = '__all__'

def upload_video_to_youtube_bg(lesson_id, temp_file_path, title, description):
    from app.lessons.models import Lesson
    
    try:
        yt_service = YouTubeService()
        result = yt_service.upload_video(
            file_path=temp_file_path,
            title=title,
            description=description
        )
        
        # Save results
        Lesson.objects.filter(id=lesson_id).update(
            youtube_video_id=result['video_id'],
            youtube_url=result['url'],
            upload_status='uploaded',
            uploaded_at=timezone.now()
        )
    except Exception:
        Lesson.objects.filter(id=lesson_id).update(
            upload_status='failed'
        )
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

from django.utils.html import format_html

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ['topic', 'group', 'date', 'start_time', 'end_time', 'upload_status', 'watch_video']
    list_filter = ['group', 'date', 'upload_status']
    search_fields = ['topic']
    readonly_fields = ['youtube_video_id', 'youtube_url', 'upload_status', 'uploaded_at', 'watch_video']

    def watch_video(self, obj):
        if obj.youtube_url:
            return format_html('<a href="{}" target="_blank" style="background:#10b981;color:white;padding:5px 10px;border-radius:4px;text-decoration:none;">▶ Ko\'rish</a>', obj.youtube_url)
        return "-"
    watch_video.short_description = "Video"

    def save_model(self, request, obj, form, change):
        video_file = form.cleaned_data.get('video_file')
        if video_file:
            # Set status to uploading
            obj.upload_status = 'uploading'
            super().save_model(request, obj, form, change)
            
            # Save uploaded file chunks to temp file
            suffix = os.path.splitext(video_file.name)[1]
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                for chunk in video_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Spawn a background thread to handle the upload to YouTube
            thread = threading.Thread(
                target=upload_video_to_youtube_bg,
                args=(
                    obj.id, 
                    temp_file_path, 
                    obj.topic or f"Lesson: {obj.topic}", 
                    f"Video lesson for group {obj.group.name}"
                )
            )
            thread.start()
            
            messages.info(request, "Video yuklash fonda (background) boshlandi. Statusni darslar ro'yxatidan kuzatishingiz mumkin.")
        else:
            super().save_model(request, obj, form, change)




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
