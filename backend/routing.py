from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/live-class/(?P<class_id>\d+)/$", consumers.LiveClassConsumer.as_asgi()),
]
