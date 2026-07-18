import os
from rest_framework import serializers

class LessonVideoUploadSerializer(serializers.Serializer):
    """
    Serializer to handle incoming video uploads for lessons.
    Performs standard client input validations.
    """
    video_file = serializers.FileField(write_only=True)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(max_length=5000, required=False, allow_blank=True)

    def validate_video_file(self, value):
        # Limit to common video formats
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}"
            )

        return value

from app.lessons.models import Lesson, Group, Course, Enrollment, Attendance, Material

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'group', 'group_name', 'date', 'start_time', 'end_time', 
            'topic', 'youtube_video_id', 'youtube_url', 'upload_status', 'uploaded_at'
        ]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'group', 'group_name', 'joined_date', 'status']

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'lesson', 'student', 'student_name', 'status', 'created_at']

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
