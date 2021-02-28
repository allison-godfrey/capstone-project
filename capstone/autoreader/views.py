from django.shortcuts import render, redirect
from .models import *
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import PersonForm
from .helpers import get_courses_for_teacher, get_courses_for_student
from django.db.models import Count

def home(request):
  if not request.user.is_authenticated:
    return redirect(reverse('autoreader:login'))

  person = Person.objects.get(user = request.user)

  if person.role == Person.Role.TEACHER:
    distinct_students = Enrollment.objects.filter(teacher = person).values('student').distinct().count()
    total_students = Enrollment.objects.filter(teacher = person).values('student').count()
    total_questions = Question.objects.filter(teacher = person).values('id').count()
    possible_responses = total_students*total_questions 
    total_responses = Response.objects.filter(teacher = person).values('id').count()
    total_assignments = Assignment.objects.filter(teacher = person).values('id').count()
    if total_assignments > 0:
      questions_per_assignment = round(total_questions/total_assignments, 1)
    else:
      questions_per_assignment = 0

    if possible_responses > 0:
      response_rate = (total_responses/possible_responses)*100
    else: 
      response_rate = 0

    if total_students > 0:
      questions_per_student = total_questions/total_students
    else:
      questions_per_student = 0

    return render(
      request,
      'autoreader/teacher/home.html',
      {'courses': get_courses_for_teacher(request),
       'user': request.user,
       'distinct_students': distinct_students,
       'total_questions': total_questions,
       'questions_per_student': questions_per_student,
       'response_rate': response_rate,
       'questions_per_assignment': questions_per_assignment}
    )
  else:
    total_courses = Enrollment.objects.filter(student = person).values('course').distinct().count()
    # get total assignments for student
    courses = map(lambda e: e.course, Enrollment.objects.filter(student = person).select_related('course'))
    assignments = []
    total_assignments = 0
    total_questions = 0
    for course in courses:
      assignments.extend(Assignment.objects.filter(course= course))
      total_assignments += Assignment.objects.filter(course= course).values('id').count()
    # get total questions assigned to student
    for assignment in assignments:
      total_questions += Question.objects.filter(assignment= assignment).values('id').count()
    
    total_responses = Response.objects.filter(student = person).values('id').count()
    # total_assignments = Assignment.objects.filter(teacher = person).values('id').count()
    unanswered = total_questions - total_responses

    if total_questions > 0:
      response_rate = (total_responses/total_questions)*100
    else: 
      response_rate = 0

    return render(
      request,
      'autoreader/student/home.html',
      {'courses': get_courses_for_student(request),
       'user': request.user,
       'total_courses': total_courses,
       'total_questions': total_questions,
       'total_assignments': total_assignments,
       'response_rate': response_rate,
       'unanswered': unanswered}
    )

def create_account(request):
  if request.method == 'POST':
    user_form = UserCreationForm(request.POST)
    person_form = PersonForm(request.POST)
    if user_form.is_valid() and person_form.is_valid():
      user = user_form.save()
      person = person_form.save(commit=False)
      person.user = user
      person.save()
      return redirect('/autoreader/')
  else:
    user_form = UserCreationForm()
    person_form = PersonForm()

  return render(
    request,
    'registration/create_account.html',
    {'user_form': user_form,
     'person_form': person_form,
     'user': request.user}
  )
