from django.shortcuts import render, redirect
from .models import *
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import PersonForm
from .helpers import get_courses_for_teacher, get_courses_for_student
from django.db.models import Count
from .assignment_calendar import AssignmentCalendar
import calendar
from datetime import datetime
from django.utils.safestring import mark_safe

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
    bar_chart_data = []
    students = set([e.student for e in Enrollment.objects.filter(teacher = person)])
    for student in students:
      question_count = 0
      response_count = 0
      enrollments = Enrollment.objects.filter(teacher = person, student = student)
      for enrollment in enrollments:
        course = enrollment.course
        question_count += Question.objects.filter(teacher = person, course_id = course.id).values('id').count()
        response_count += Response.objects.filter(teacher = person, course_id = course.id, student = student).values('id').count()
      student_rate = (response_count/question_count)*100
      if student_rate < 33:
        color = 'danger'
      elif student_rate >= 33 and student_rate <= 66:
        color = 'warning'
      else:
        color = 'success'
      
      bar_chart_data.append((
        student.user.username, 
        student_rate,
        color,
        question_count - response_count))

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
       'questions_per_assignment': questions_per_assignment,
       'bar_chart_data': bar_chart_data}
    )
  else:
    total_courses = Enrollment.objects.filter(student = person).values('course').distinct().count()
    # get total assignments for student
    courses = map(lambda e: e.course, Enrollment.objects.filter(student = person).select_related('course'))
    assignments = []
    # a list of tuples, where each tuple is like (assignment, course, percent complete, color, questions remaining)
    bar_chart_data = []
    total_assignments = 0
    total_questions = 0
    for course in courses:
      assignments.extend(Assignment.objects.filter(course= course))
      total_assignments += Assignment.objects.filter(course= course).values('id').count()
    # get total questions assigned to student
    for assignment in assignments:
      question_count = Question.objects.filter(assignment= assignment).values('id').count()
      total_questions += question_count
      response_count = Response.objects.filter(student = person, assignment= assignment).values('id').count()
      if question_count > 0:
        response_rate = int(100 * float(response_count) / question_count)
      else:
        response_rate = 0

      if response_rate < 33:
        color = 'danger'
      elif response_rate >= 33 and response_rate <= 66:
        color = 'warning'
      else:
        color = 'success'

      bar_chart_data.append((
        assignment,
        assignment.course,
        response_rate,
        color,
        question_count - response_count,
      ))
    
    total_responses = Response.objects.filter(student = person).values('id').count()
    # total_assignments = Assignment.objects.filter(teacher = person).values('id').count()
    unanswered = total_questions - total_responses

    if total_questions > 0:
      response_rate = (total_responses/total_questions)*100
    else: 
      response_rate = 0

    # calendar = HTMLCalendar()
    today = datetime.now().date()
    # calendar.cssclasses_weekday_head = ['weekday-header'] * 7
    # calendar = calendar.formatmonth(today.year, today.month, withyear = True)
    # calendar = calendar.replace('<td ', '<td style="width: 150px; height: 150px"')
    assignments_due_this_month = [a for a in assignments if a.due_date.month == today.month and a.due_date.year == today.year]
    current_assignment_calendar = AssignmentCalendar(assignments = assignments_due_this_month)
    current_calendar = current_assignment_calendar.formatmonth(today.year, today.month)
    if today.month == 12:
      next_month = 1
      next_year = today.year + 1
    else:
      next_month = today.month + 1
      next_year = today.year
    assignments_due_next_month = [a for a in assignments if a.due_date.month == next_month and a.due_date.year == next_year]
    next_assignment_calendar = AssignmentCalendar(assignments = assignments_due_next_month, is_current_month = False)
    next_calendar = next_assignment_calendar.formatmonth(next_year, next_month)

    return render(
      request,
      'autoreader/student/home.html',
      {'courses': get_courses_for_student(request),
       'user': request.user,
       'total_courses': total_courses,
       'total_questions': total_questions,
       'total_assignments': total_assignments,
       'response_rate': response_rate,
       'unanswered': unanswered,
       'bar_chart_data': bar_chart_data,
       'current_calendar': mark_safe(current_calendar),
       'current_month_year': calendar.month_name[today.month] + ' ' + str(today.year),
       'next_calendar': mark_safe(next_calendar),
       'next_month_year': calendar.month_name[next_month] + ' ' + str(next_year)}
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
