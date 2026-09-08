from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import Assignment, ChecklistItem, Project, Status, Tag, Task, TaskMetrics


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_final")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    autocomplete_fields = ("owner",)


@admin.register(Task)
class TaskAdmin(MPTTModelAdmin):
    """Admin arborescent (tâches / sous-tâches)."""
    list_display = ("name", "project", "status", "parent")
    list_filter = ("status", "priority", "project")
    search_fields = ("name",)


admin.site.register(TaskMetrics)
