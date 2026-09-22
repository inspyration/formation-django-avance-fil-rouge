from django.urls import path

from . import views

app_name = "tasks"
urlpatterns = [
    path("tasks/", views.task_list, name="task_list"),
    path("mes-taches/", views.my_tasks, name="my_tasks"),
    path("mes-projets/", views.my_projects, name="my_projects"),
    path("tableau-de-bord/", views.dashboard, name="dashboard"),
    path("stats/", views.public_stats, name="public_stats"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/pdf/", views.task_pdf, name="task_pdf"),
    path("tasks/<int:pk>/status/", views.task_set_status, name="task_set_status"),
    path("htmx/search/", views.task_search, name="task_search"),
    path("htmx/assignees/", views.assignees_options, name="assignees_options"),
    path("htmx/justification/", views.justification_field, name="justification_field"),
    path("htmx/checklist-row/", views.checklist_add_row, name="checklist_add_row"),
    path("location/", views.geo_cascade, name="geo_cascade"),
    path("htmx/regions/", views.geo_regions, name="geo_regions"),
    path("htmx/subregions/", views.geo_subregions, name="geo_subregions"),
    path("htmx/cities/", views.geo_cities, name="geo_cities"),
    path("projects/<int:project_id>/kanban/", views.kanban, name="kanban"),
    path("location/vue/", views.geo_advanced, name="geo_advanced"),
]
