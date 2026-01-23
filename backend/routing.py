from django.urls import re_path

from . import consumers
from backend.live_class import consumers as ai_consumers

websocket_urlpatterns = [
    re_path(r"ws/live-class/(?P<class_id>\d+)/$", consumers.LiveClassConsumer.as_asgi()),
    re_path(r"ws/ai/live-class/(?P<class_id>\d+)/$", ai_consumers.AIClassConsumer.as_asgi()),
]
