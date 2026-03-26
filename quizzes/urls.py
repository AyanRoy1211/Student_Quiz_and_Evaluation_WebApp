from django.urls import path
from . import views

urlpatterns = [
    # Instructor
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<int:quiz_id>/questions/', views.quiz_add_question, name='quiz_add_question'),
    path('question/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),

    # Student
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('browse/', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
]
