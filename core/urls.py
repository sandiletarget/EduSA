from django.urls import include, path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("choose-role/", views.choose_role, name="choose_role"),

    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/add/", views.lesson_create, name="lesson_add"),
    path("teacher/edit/<int:pk>/", views.lesson_edit, name="lesson_edit"),
    path("teacher/delete/<int:pk>/", views.lesson_delete, name="lesson_delete"),
    path("teacher/exams/add/", views.exam_create, name="exam_add"),

    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/join-class/", views.join_class, name="join_class"),
    path("classes/", include("classes.urls")),
    path('teacher/quiz-results/', views.teacher_quiz_results, name='teacher_quiz_results'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
    path("", include("lessons.urls")),
]
