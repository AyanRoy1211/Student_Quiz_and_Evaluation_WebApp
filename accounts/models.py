from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_instructor(self):
        return self.role == 'instructor'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_admin_user(self):
        return self.role == 'admin'
