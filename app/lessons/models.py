from django.db import models
from app.common.models import BaseModel
from app.users.models import User

class Course(BaseModel):
    name = models.CharField('Course name', max_length=255)
    description = models.TextField('Description', blank=True, null=True)
    monthly_price = models.DecimalField('Monthly price', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Group(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups', verbose_name='Course')
    teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='teaching_groups', 
        limit_choices_to={'role': User.RoleChoices.TEACHER},
        verbose_name='Teacher'
    )
    name = models.CharField('Group name', max_length=255)
    schedule = models.CharField('Schedule', max_length=255, help_text="e.g. Mon/Wed/Fri 14:00")
    status = models.CharField('Status', max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        indexes = [
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.course.name}"

class Enrollment(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DROPPED = 'dropped', 'Dropped'

    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        limit_choices_to={'role': User.RoleChoices.STUDENT},
        verbose_name='Student'
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Group')
    joined_date = models.DateField('Joined date', auto_now_add=True)
    status = models.CharField('Status', max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ('student', 'group')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['joined_date']),
        ]

    def __str__(self):
        return f"{self.student.username} -> {self.group.name}"

class Lesson(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons', verbose_name='Group')
    date = models.DateField('Date')
    start_time = models.TimeField('Start time', null=True, blank=True)
    end_time = models.TimeField('End time', null=True, blank=True)
    topic = models.CharField('Topic', max_length=255)

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.topic} ({self.group.name} - {self.date})"

class Attendance(BaseModel):
    class StatusChoices(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances', verbose_name='Lesson')
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='attendances', 
        limit_choices_to={'role': User.RoleChoices.STUDENT},
        verbose_name='Student'
    )
    status = models.CharField('Status', max_length=20, choices=StatusChoices.choices, default=StatusChoices.PRESENT)

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = ('lesson', 'student')
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.lesson.topic} - {self.status}"

class Material(BaseModel):
    class TypeChoices(models.TextChoices):
        VIDEO = 'video', 'Video'
        PDF = 'pdf', 'PDF'
        AUDIO = 'audio', 'Audio'
        IMAGE = 'image', 'Image'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', verbose_name='Course')
    title = models.CharField('Title', max_length=255)
    telegram_file_id = models.CharField('Telegram file ID', max_length=255)
    type = models.CharField('Type', max_length=10, choices=TypeChoices.choices, default=TypeChoices.PDF)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
