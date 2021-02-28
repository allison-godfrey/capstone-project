from django import forms
from django.forms import ModelForm
from .models import Person, Course, Assignment, Question, Response
from .helpers import validate_course_code

class PersonForm(ModelForm):
  class Meta:
    model = Person
    fields = ("role",)

class CourseForm(ModelForm):
	class Meta:
		model = Course
		fields = ("course_name", "description")
		# to change label shown in form:
		# labels = {'course_name': 'Enter course name'}
		# see https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#overriding-the-default-fields
		# for more

class AssignmentForm(ModelForm):
	class Meta:
		model = Assignment
		fields = ("assignment_name", "description")

class QuestionForm(ModelForm):
	class Meta:
		model = Question
		fields = ("question_name", "description")

class JoinCourseForm(forms.Form):
	course_code = forms.CharField(max_length=7, validators = [validate_course_code])

class ResponseForm(ModelForm):
	class Meta:
		model = Response
		fields = ("response",)