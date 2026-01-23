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
    path("student/progress/", views.student_progress, name="student_progress"),
    path("lessons/catalog/", views.lesson_catalog, name="lesson_catalog"),
    path("lessons/<int:pk>/", views.lesson_detail, name="lesson_detail"),
    path("lessons/slug/<slug:slug>/", views.lesson_detail_slug, name="lesson_detail_slug"),
    path("exams/", views.exam_list, name="exam_list"),
    path("exams/<int:exam_id>/take/", views.exam_take, name="exam_take"),
    path("exams/result/<int:attempt_id>/", views.exam_result, name="exam_result"),
    path("api/courses/", views.course_list_api, name="course_list_api"),
    path("api/courses/<int:course_id>/", views.course_detail_api, name="course_detail_api"),
    path("api/notifications/", views.notifications_api, name="notifications_api"),
    path("api/formulas/", views.formulas_api, name="formulas_api"),
    path("api/lessons/", views.lessons_api, name="lessons_api"),
    path("api/exams/", views.exams_api, name="exams_api"),
    path("classes/", include("classes.urls")),
    path('teacher/quiz-results/', views.teacher_quiz_results, name='teacher_quiz_results'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
    path("", include("lessons.urls")),
]
