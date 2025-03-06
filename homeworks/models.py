import uuid
from django.db import models
from users.models import Student
from django.core.validators import MaxValueValidator, MinValueValidator

class CustomHomeworkManager(models.Manager):
    def create_homework(self, student, week_number, **extra_fields):
        if not student:
            raise ValueError('The Student field must be set')
        if week_number is None:
            raise ValueError('The week_number field must be set')

        homework = self.model(
            student=student,
            week_number=week_number,
            **extra_fields
        )
        homework.save(using=self._db)
        return homework

class Homework(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    week_number = models.IntegerField(validators=[MaxValueValidator(30)]) 
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)], default=0)
    score_created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomHomeworkManager()

    def __str__(self):
        return f"Homework for {self.student} - Week {self.week_number}"

def homework_picture_upload_to(instance, filename):
    # Access the homework and its associated student
    student_id = instance.homework.student.id
    return f'homework_pictures/{student_id}/{filename}'

class HomeworkPicture(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to=homework_picture_upload_to)
    description = models.CharField(max_length=1000, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for Homework ID: {self.homework.id}"
