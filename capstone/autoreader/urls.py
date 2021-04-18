from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import teacher_views
from . import student_views

app_name = 'autoreader'

teacher_urls = [
  path('create_course/', teacher_views.create_course, name='create_course'),
  path('courses/<int:course_id>/', teacher_views.course, name='courses'),
  path('courses/<int:course_id>/create_assignment/', teacher_views.create_assignment, name='create_assignment'),
  path('courses/<int:course_id>/assignments/<int:assignment_id>/', teacher_views.assignment, name='assignment'),
  path('courses/<int:course_id>/assignments/<int:assignment_id>/questions/<int:question_id>', teacher_views.question, name='question'),
  path('courses/<int:course_id>/assignments/<int:assignment_id>/create_question', teacher_views.create_question, name='create_question'),
  path('courses/<int:course_id>/assignments/<int:assignment_id>/questions/<int:question_id>/responses/<int:response_id>', teacher_views.feedback, name='feedback'),
]

student_urls = [
	path('join_course/', student_views.join_course, name='join_course'),
  path('student/courses/<int:course_id>', student_views.course, name='student_course'),
  path('student/courses/<int:course_id>/assignments/<int:assignment_id>/questions/<int:question_id>', student_views.question, name='student_question'),
  path('student/courses/<int:course_id>/assignments/<int:assignment_id>/questions/<int:question_id>/responses/<int:response_id>', student_views.update_response, name='update_response'),
  path('student/courses/<int:course_id>/assignments/<int:assignment_id>/', student_views.assignment, name='student_assignment'),
]

urlpatterns = [
  path('', views.home, name = 'home'),
  path('accounts/', include('django.contrib.auth.urls')),
  path('accounts/create_account/', views.create_account, name='create_account'),
] + teacher_urls + student_urls + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
