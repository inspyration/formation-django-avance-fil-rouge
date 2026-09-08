from django.urls import path

from . import views

app_name = "tasks"
urlpatterns = [
    path("tasks/<int:pk>/pdf/", views.task_pdf, name="task_pdf"),
]
