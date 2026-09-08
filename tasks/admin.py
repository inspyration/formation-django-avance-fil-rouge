from django.contrib import admin

from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from .models import (
    Action,
    Anomaly,
    Assignment,
    ChecklistItem,
    Improvement,
    Project,
    Status,
    Tag,
    Task,
    TaskMetrics,
)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_final", "color")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    autocomplete_fields = ("owner",)


class TaskChildAdmin(PolymorphicChildModelAdmin):
    """Base des admins enfants."""
    base_model = Task
    list_display = ("name", "project", "status", "priority")


@admin.register(Anomaly)
class AnomalyAdmin(TaskChildAdmin):
    base_model = Anomaly
    show_in_index = True


@admin.register(Action)
class ActionAdmin(TaskChildAdmin):
    base_model = Action
    show_in_index = True


@admin.register(Improvement)
class ImprovementAdmin(TaskChildAdmin):
    base_model = Improvement
    show_in_index = True


@admin.register(Task)
class TaskParentAdmin(PolymorphicParentModelAdmin):
    base_model = Task
    child_models = (Task, Anomaly, Action, Improvement)
    list_filter = (PolymorphicChildModelFilter, "status", "priority")
    list_display = ("name", "project", "status", "priority")
    search_fields = ("name",)


admin.site.register(TaskMetrics)
