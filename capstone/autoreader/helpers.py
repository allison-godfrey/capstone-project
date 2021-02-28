from .models import Person, Course, Assignment, Question, Enrollment
from django.core.exceptions import ValidationError

def is_teacher(user):
  try:
    person = Person.objects.get(user=user)
  except Person.DoesNotExist:
    return False

  return person.role == Person.Role.TEACHER

def is_student(user):
  try:
    person = Person.objects.get(user=user)
  except Person.DoesNotExist:
    return False

  return person.role == Person.Role.STUDENT

def get_courses_for_teacher(request):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  courses = Course.objects.filter(teacher = person)

  return courses

def get_courses_for_student(request):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  enrollments = Enrollment.objects.filter(student = person)

  return [e.course for e in enrollments]

def get_assignments(request, course_id):
  course = Course.objects.get(id=course_id)
  assignments = Assignment.objects.filter(course = course)
  return assignments

def get_questions(request, assignment_id):
  assignment = Assignment.objects.get(id=assignment_id)
  questions = Question.objects.filter(assignment = assignment)
  return questions

def validate_course_code(course_code):
  if not Course.objects.filter(code = course_code).exists():
    raise ValidationError(course_code + ' is not a valid course code.')

def get_students(course):
  enrollments = Enrollment.objects.filter(course = course)
  students = []
  for enrollment in enrollments:
    student = enrollment.student
    students.append(student)
  return students

  
