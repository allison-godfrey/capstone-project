from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .helpers import *
from .forms import JoinCourseForm, ResponseForm
from .models import *

@login_required
@user_passes_test(is_student)
def join_course(request):
	if request.method == 'POST':
		join_course_form = JoinCourseForm(request.POST)
		if join_course_form.is_valid():
			course = Course.objects.get(code = join_course_form.cleaned_data['course_code'])
			person = Person.objects.get(user = request.user)
			enrollment = Enrollment(student = person, course = course, teacher = course.teacher)
			enrollment.save()
			return redirect(reverse('autoreader:student_course', args=[course.id]))
	else:
		join_course_form = JoinCourseForm()

	return render(
		request,
		'autoreader/student/join_course.html',
		{'courses': get_courses_for_student(request),
			'join_course_form': join_course_form,
			'user': request.user}
	)

@login_required
@user_passes_test(is_student)
def course(request, course_id):
	course = Course.objects.get(pk = course_id)

	return render(
		request,
		'autoreader/student/course.html',
		{'courses': get_courses_for_student(request),
			'course': course,
			'user': request.user,
			'assignments': get_assignments(request, course_id),}
	)

@login_required
@user_passes_test(is_student)
def assignment(request, course_id, assignment_id):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  assignment = get_object_or_404(Assignment, pk=assignment_id)
  response_form = ResponseForm()

  questions = get_questions(request, assignment_id)
  # responses is a map from question ID to a boolean indicating whether or not the student
  # has responded to that question
  # e.g. {1: true, 2: false} means the student has responded to question 1 but not question 2
  responses = []

  for question in questions:
  	if Response.objects.filter(question_id = question.id, student_id = person.id).exists():
  		responses.append(True)
  	else:
  		responses.append(False)

  return render(
    request,
    'autoreader/student/assignment.html',
    {'course_id': course_id,
     'courses': get_courses_for_student(request),
     'assignment': assignment,
     'questions': zip(get_questions(request, assignment_id), responses),
     'user': request.user,
     'response_form': response_form}
  )

@login_required
@user_passes_test(is_student)
def question(request, course_id, assignment_id, question_id):
	if request.method == 'POST':
		response_form = ResponseForm(request.POST, request.FILES)
		if response_form.is_valid():
			course = Course.objects.get(id = course_id)
			person = Person.objects.get(user=request.user)
			response = response_form.save(commit = False)
			response.student = person
			response.course_id = course_id
			response.assignment_id = assignment_id
			response.question_id = question_id
			response.teacher = course.teacher
			response.save()
			return redirect(reverse('autoreader:student_assignment', args=[course_id, assignment_id]))
	else:
		response_form = ResponseForm()

	return render(
		request,
		'autoreader/student/question.html',
		{'courses': get_courses_for_student(request),
			'response_form': response_form,
			'course_id': course_id,
			'assignment_id': assignment_id,
			'question_id': question_id,
			'user': request.user}
	)