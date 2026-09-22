from django.contrib import admin
from django.db.models import Q

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
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_final", "color")
    list_editable = ("order", "is_final")
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

    def get_queryset(self, request):
        """Visibilité métier : un superadmin voit tout ; sinon on ne voit que
        SES projets (dont on est propriétaire ou membre de l'équipe)."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        u = request.user
        return qs.filter(Q(owner=u) | Q(members=u)).distinct()


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


# Fieldsets sur-mesure : on regroupe et, de temps en temps, on met PLUSIEURS
# champs sur la même ligne (tuple imbriqué dans "fields").
FIELDSETS_SUPERUSER = (
    (None, {"fields": ("name", "slug", ("status", "priority", "task_kind"), "description")}),
    ("Planning", {"fields": (("target_datetime", "actual_end_datetime"), "delay",
                             ("progress", "scrum_points"))}),
    ("Rattachement", {"fields": ("project", ("created_by", "original_task"), "tags")}),
    ("Facturation", {"fields": (("is_billable", "estimated_cost"), "estimated_duration")}),
    ("Divers", {"fields": ("reference_url", "reporter_email", "metadata",
                           ("attachment", "cover"))}),
    ("Suivi", {"classes": ("collapse",),
               "fields": ("public_id", ("created_at", "updated_at"))}),
)

# Vue allégée et tailored pour un membre d'équipe (staff non-superadmin) :
# l'essentiel, avec plusieurs champs par ligne là où c'est pertinent.
FIELDSETS_STAFF = (
    (None, {"fields": ("name", ("status", "priority"), "description")}),
    ("Planning", {"fields": (("target_datetime", "actual_end_datetime"), "delay", "progress")}),
    ("Rattachement", {"fields": ("project", "created_by")}),
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "priority", "created_by", "target_datetime")
    list_filter = ("status", "priority", "project", "task_kind")
    search_fields = ("name", "description")
    autocomplete_fields = ("project", "status", "tags", "created_by", "original_task")
    readonly_fields = ("public_id", "delay", "created_at", "updated_at")
    inlines = [ChecklistItemInline, AssignmentInline]
    actions = [duplicate_tasks]

    def get_queryset(self, request):
        """Visibilité métier : un superadmin voit tout ; sinon on ne voit que
        SES tâches — celles de ses projets (propriétaire ou membre d'équipe),
        plus celles qu'on a créées ou qui nous sont affectées."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        u = request.user
        return qs.filter(
            Q(project__owner=u) | Q(project__members=u)
            | Q(created_by=u) | Q(assignees=u)
        ).distinct()

    def get_fieldsets(self, request, obj=None):
        """Fieldsets sur-mesure : jeu complet pour un superadmin, vue allégée
        pour un membre d'équipe."""
        if request.user.is_superuser:
            return FIELDSETS_SUPERUSER
        return FIELDSETS_STAFF


admin.site.register(TaskMetrics)
