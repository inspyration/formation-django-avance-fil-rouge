from django.urls import path

from . import views

app_name = "tasks"
urlpatterns = [
    path("tasks/", views.task_list, name="task_list"),
    path("mes-taches/", views.my_tasks, name="my_tasks"),
    path("mes-projets/", views.my_projects, name="my_projects"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/pdf/", views.task_pdf, name="task_pdf"),
    path("tasks/<int:pk>/status/", views.task_set_status, name="task_set_status"),
    path("htmx/search/", views.task_search, name="task_search"),
    path("htmx/assignees/", views.assignees_options, name="assignees_options"),
    path("htmx/justification/", views.justification_field, name="justification_field"),
    path("htmx/checklist-row/", views.checklist_add_row, name="checklist_add_row"),
]
