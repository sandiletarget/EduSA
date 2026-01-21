from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    path("create/", views.create_class, name="class_create"),
    path("<int:pk>/", views.class_detail, name="class_detail"),
    path("<int:pk>/live/start/", views.start_live_session, name="start_live_session"),
    path("<int:pk>/live/join/", views.join_live_session, name="join_live_session"),
    path("<int:pk>/live/room/", views.live_class_room, name="live_class_room"),
    path("<int:pk>/assessments/", views.assessment_list, name="assessment_list"),
    path("<int:pk>/assessments/create/", views.assessment_create, name="assessment_create"),
    path("assessments/<int:assessment_id>/submit/", views.assessment_submit, name="assessment_submit"),
    path("join/", views.join_class, name="join_class")
]
