import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, verification_code, full_name, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        if full_name is None:
            raise ValueError('The Fullname field must be set')

        user = self.model(
            phone=phone,
            full_name=full_name,
            **extra_fields
        )
        user.set_password(verification_code)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, verification_code, full_name, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)  # Ensure superuser is also staff
        return self.create_user(phone, verification_code, full_name, **extra_fields)

def user_profile_path(instance, filename):
    return f'profiles/{instance.id}/{filename}'

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=30)
    profile = models.ImageField(upload_to=user_profile_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)  

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.full_name}"



class Coaches(User):

    class Meta:
        permissions = [
            ("can_access_coach_endpoint", "Can access coach endpoint"),
        ]


class Student(User):
    course = models.IntegerField()  # Assuming this is a course ID

    class Meta:
        permissions = [
            ("can_access_student_endpoint", "Can access student endpoint"),
        ]
