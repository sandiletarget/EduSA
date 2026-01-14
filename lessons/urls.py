from django.urls import path

from . import views, views_student

urlpatterns = [
    path('student/lessons/', views_student.student_lesson_list, name='student_lessons'),
    path('student/lessons/<int:pk>/', views_student.student_lesson_detail, name='student_lesson_detail'),
    path('student/lessons/<int:pk>/complete/', views_student.mark_lesson_complete, name='mark_lesson_complete'),
    path('student/lesson/<int:lesson_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('student/certificate/<int:result_id>/', views.certificate_view, name='certificate'),
    path('teacher/grade-analytics/', views.grade_level_analytics, name='grade_level_analytics'),
    path('classes/<int:class_id>/lessons/', views.class_lesson_list, name='class_lesson_list'),
]
