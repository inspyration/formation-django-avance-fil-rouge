from django.urls import path

from .consumers import BoardConsumer

websocket_urlpatterns = [
    path("ws/board/<int:project_id>/", BoardConsumer.as_asgi()),
]
