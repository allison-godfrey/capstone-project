import datetime
import string
import random

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Person(models.Model):
  class Role(models.TextChoices):
    STUDENT = 'student'
    TEACHER = 'teacher'

  user = models.OneToOneField(User, on_delete=models.CASCADE)
  role = models.CharField(max_length=100, choices=Role.choices)


class Course(models.Model):
  teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
  course_name = models.CharField(max_length=100)
  description = models.CharField(max_length=200)
  code = models.CharField(max_length=10, unique=True)

  def _random_code(self):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

  def save(self, *args, **kwargs):
    if self._state.adding:
      self.code = self._random_code()
    super(Course, self).save(*args, **kwargs)

class Assignment(models.Model):
  teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
  course = models.ForeignKey(Course, on_delete=models.CASCADE)
  assignment_name = models.CharField(max_length=100)
  description = models.CharField(max_length=200)

class Question(models.Model):
  teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
  course = models.ForeignKey(Course, on_delete=models.CASCADE)
  assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
  question_name = models.CharField(max_length=600)
  description = models.CharField(max_length=200)

class Enrollment(models.Model):
  student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name = 'enrollment_student')
  course = models.ForeignKey(Course, on_delete=models.CASCADE)
  teacher = models.ForeignKey(Person, on_delete=models.CASCADE, related_name = 'enrollment_teacher')

class Response(models.Model):
  student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name = 'response_student')
  teacher = models.ForeignKey(Person, on_delete=models.CASCADE, related_name = 'response_teacher')
  course = models.ForeignKey(Course, on_delete=models.CASCADE)
  assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  response = models.ImageField()
