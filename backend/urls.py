from django.urls import path

from . import views

app_name = "backend"

urlpatterns = [
    path("classes/<int:class_id>/live/", views.live_class_room, name="live_class_room"),
]
