from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    path("create/", views.create_class, name="class_create"),
    path("<int:pk>/", views.class_detail, name="class_detail"),
    path("<int:pk>/live/start/", views.start_live_session, name="start_live_session"),
    path("<int:pk>/live/join/", views.join_live_session, name="join_live_session"),
    path("join/", views.join_class, name="join_class")
]
