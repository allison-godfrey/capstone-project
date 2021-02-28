from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import *
from .forms import PersonForm, CourseForm, AssignmentForm, QuestionForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .helpers import *

import cv2
from .htr.src.DataLoaderIAM import DataLoaderIAM, Batch
from .htr.src.SamplePreprocessor import preprocess
from .htr.src.Model import Model, DecoderType

@login_required
@user_passes_test(is_teacher)
def create_course(request):
  if request.method == 'POST':
    course_form = CourseForm(request.POST)
    if course_form.is_valid():
      course = course_form.save(commit = False)
      try:
        person = Person.objects.get(user=request.user)
      except Person.DoesNotExist:
        return redirect('/autoreader/')

      course.teacher = person
      course.save()
      return redirect(reverse('autoreader:courses', args=[course.id]))
  else:
    course_form = CourseForm()

  return render(
    request,
    'autoreader/teacher/create_course.html',
    {'course_form': course_form,
     'courses': get_courses_for_teacher(request),
     'user': request.user}
  )

@login_required
@user_passes_test(is_teacher)
def create_assignment(request, course_id):
  if request.method == 'POST':
    assignment_form = AssignmentForm(request.POST)
    if assignment_form.is_valid():
      assignment = assignment_form.save(commit = False)
      try:
        person = Person.objects.get(user = request.user)
        course = Course.objects.get(id = course_id)
      except Person.DoesNotExist:
        return redirect('/autoreader/')

      assignment.teacher = person
      assignment.course = course
      assignment.save()
      return redirect(reverse('autoreader:courses', args=[course_id]))
  else:
    assignment_form = AssignmentForm()

  return render(
    request,
    'autoreader/teacher/create_assignment.html',
    {'assignment_form': assignment_form,
     'courses': get_courses_for_teacher(request),
     'user': request.user,
     'course_id': course_id}
  )

@login_required
@user_passes_test(is_teacher)
def create_question(request, course_id, assignment_id):
  if request.method == 'POST':
    question_form = QuestionForm(request.POST)
    if question_form.is_valid():
      question = question_form.save(commit = False)
      try:
        person = Person.objects.get(user=request.user)
        course = Course.objects.get(id = course_id)
        assignment = Assignment.objects.get(id = assignment_id)

      except Person.DoesNotExist:
        return redirect('/autoreader/')

      question.teacher = person
      question.course = course
      question.assignment = assignment
      question.save()
      return redirect(reverse('autoreader:assignment', args=[course_id, assignment_id]))
  else:
    question_form = QuestionForm()

  return render(
    request,
    'autoreader/teacher/create_question.html',
    {'question_form': question_form,
     'courses': get_courses_for_teacher(request),
     'assignment_id': assignment_id,
     'user': request.user,
     'course_id': course_id}
  )


@login_required
@user_passes_test(is_teacher)
def course(request, course_id):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  course = get_object_or_404(Course, pk=course_id, teacher=person)

  return render(
    request,
    'autoreader/teacher/course.html',
    {'course': course,
     'courses': get_courses_for_teacher(request),
     'assignments': get_assignments(request, course_id),
     'user': request.user,
     'students': get_students(course)}
  )

@login_required
@user_passes_test(is_teacher)
def assignment(request, course_id, assignment_id):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  assignment = get_object_or_404(Assignment, pk=assignment_id, teacher=person)

  return render(
    request,
    'autoreader/teacher/assignment.html',
    {'course_id': course_id,
     'courses': get_courses_for_teacher(request),
     'assignment': assignment,
     'questions': get_questions(request, assignment_id),
     'user': request.user}
  )

@login_required
@user_passes_test(is_teacher)
def question(request, course_id, assignment_id, question_id):
  try:
    person = Person.objects.get(user=request.user)
  except Person.DoesNotExist:
    return redirect('/autoreader/')

  question = get_object_or_404(Question, pk=question_id, teacher=person)
  responses = Response.objects.filter(question_id = question.id).select_related('student__user')
  texts = []
  for response in responses:
    # pass image to the model to get extracted text
    model = Model(open('autoreader/htr/model/charList.txt').read(), DecoderType.BestPath, mustRestore=True, dump=False)
    "recognize text in image provided by file path"
    img = preprocess(cv2.imread(response.response.path, cv2.IMREAD_GRAYSCALE), Model.imgSize)
    batch = Batch(None, [img])  
    (recognized, probability) = model.inferBatch(batch, True)
    texts.append(recognized[0])

  return render(
    request,
    'autoreader/teacher/question.html',
    {'course': course,
     'courses': get_courses_for_teacher(request),
     'user': request.user,
     'question': question,
     'responses': zip(responses, texts)}
  )
