from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from adminsortable2.admin import SortableAdminMixin

from .models import (
    Assignment,
    ChecklistItem,
    Project,
    Status,
    Tag,
    Task,
    TaskMetrics,
)


@admin.register(Status)
class StatusAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Ordre des statuts géré par glisser-déposer (adminsortable2)."""
    list_display = ("name", "order", "is_final", "color")
    list_editable = ("is_final",)  # 'order' est piloté par le drag-and-drop
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("owner",)


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1
    autocomplete_fields = ("user",)


@admin.action(description="Dupliquer les tâches sélectionnées")
def duplicate_tasks(modeladmin, request, queryset):
    count = 0
    for task in queryset:
        task.duplicate()
        count += 1
    modeladmin.message_user(request, f"{count} tâche(s) dupliquée(s).")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "priority", "created_by", "target_datetime")
    list_filter = (
        ("project", RelatedDropdownFilter),
        "status", "priority", "task_kind",
    )
    search_fields = ("name", "description")
    autocomplete_fields = ("project", "status", "tags", "created_by", "original_task")
    readonly_fields = ("public_id", "delay", "created_at", "updated_at")
    inlines = [ChecklistItemInline, AssignmentInline]
    actions = [duplicate_tasks]


admin.site.register(TaskMetrics)
