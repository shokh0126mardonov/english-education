from django.db import models
from app.common.models import BaseModel
from app.users.models import User

class Course(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Group(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_groups')
    name = models.CharField(max_length=255)
    schedule = models.CharField(max_length=255, help_text="e.g. Mon/Wed/Fri 14:00")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    def __str__(self):
        return f"{self.name} - {self.course.name}"

class Enrollment(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DROPPED = 'dropped', 'Dropped'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='enrollments')
    joined_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    def __str__(self):
        return f"{self.student.username} -> {self.group.name}"

class Lesson(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')
    date = models.DateField()
    topic = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.topic} ({self.group.name} - {self.date})"

class Attendance(BaseModel):
    class StatusChoices(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PRESENT)

    def __str__(self):
        return f"{self.student.username} - {self.lesson.topic} - {self.status}"

class Material(BaseModel):
    class TypeChoices(models.TextChoices):
        VIDEO = 'video', 'Video'
        PDF = 'pdf', 'PDF'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    telegram_file_id = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TypeChoices.choices, default=TypeChoices.PDF)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
