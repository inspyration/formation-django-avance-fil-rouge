import uuid

from django.conf import settings
from django.db import models

from .enums import Priority, TaskKind, task_kind_choices
from .mixins import OrderingMixin, TrackingMixin


class Project(TrackingMixin):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="projects"
    )
    # Team members (non-superusers) allowed to access the project.
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="member_projects",
        limit_choices_to={"is_superuser": False},
    )

    def __str__(self):
        return self.name


class Status(OrderingMixin):
    name = models.CharField(max_length=100)
    is_final = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default="#888888")

    class Meta:
        ordering = ["order"]
        verbose_name = "statut"
        verbose_name_plural = "statuts"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    def __str__(self):
        return self.name


class Task(TrackingMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, blank=True)
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices, default=Priority.MEDIUM
    )
    task_kind = models.CharField(
        max_length=20, choices=task_kind_choices(), default=TaskKind.FEATURE.value
    )
    scrum_points = models.PositiveSmallIntegerField(default=0)
    progress = models.FloatField(default=0.0)
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    estimated_duration = models.DurationField(null=True, blank=True)
    target_datetime = models.DateTimeField(null=True, blank=True)
    actual_end_datetime = models.DateTimeField(null=True, blank=True)
    # Nouveauté Django 5.0 : db_default pose un DEFAULT en base. Contrairement
    # à default (appliqué par Django à la création de l'objet), il vaut aussi
    # pour un INSERT en SQL brut, hors ORM.
    is_billable = models.BooleanField(default=False, db_default=False)
    reference_url = models.URLField(blank=True)
    reporter_email = models.EmailField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    cover = models.ImageField(upload_to="covers/", null=True, blank=True)
    # Database-generated stored column (Django 5.0 feature): delay = actual end - target.
    delay = models.GeneratedField(
        expression=models.F("actual_end_datetime") - models.F("target_datetime"),
        output_field=models.DurationField(),
        db_persist=True,
    )
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name="tasks")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="created_tasks",
    )
    original_task = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="duplicates"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Assignment", related_name="assigned_tasks"
    )

    class Meta:
        ordering = ["-created_at"]
        # Nouveauté Django 5.1 : l'argument s'appelle « condition » (avant : « check »,
        # supprimé en 6.0). Une CheckConstraint est opposable EN BASE — y compris à un
        # bulk_create ou un script de reprise, là où un validator ne protège que les
        # formulaires.
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progress__gte=0) & models.Q(progress__lte=100),
                name="task_progress_entre_0_et_100",
            ),
        ]
        # Index composites. L'ordre des colonnes suit l'ordre des filtres : le premier
        # sert « project », puis « project ET status » — jamais « status » seul.
        # Le second est PARTIEL (condition=) : il n'indexe que les tâches en cours,
        # donc plus petit et plus rapide (PostgreSQL, SQLite).
        indexes = [
            models.Index(fields=["project", "status"], name="task_projet_statut_idx"),
            models.Index(
                fields=["project"],
                condition=models.Q(actual_end_datetime__isnull=True),
                name="task_en_cours_idx",
            ),
        ]

    def __str__(self):
        return self.name


class Assignment(models.Model):
    ROLES = [
        ("owner", "Responsable"),
        ("contributor", "Contributeur"),
        ("reviewer", "Relecteur"),
    ]
    # Nouveauté Django 5.2 : la clé primaire est le couple (task, user). Plus de
    # colonne « id », et l'unicité est native — la UniqueConstraint devient inutile.
    #
    # POURQUOI CE N'EST PAS LE CHOIX DE main : un modèle à clé composite ne peut
    # pas être la cible d'une ForeignKey, et l'admin ne le gère pas partout. Sur le
    # fil rouge, Assignment reste une table d'association classique. On la montre
    # ici, en démonstration isolée, précisément pour exposer ces limites.
    pk = models.CompositePrimaryKey("task", "user")
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default="contributor")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} / {self.task} ({self.role})"


class ChecklistItem(OrderingMixin):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="checklist")
    label = models.CharField(max_length=255)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label


class TaskMetrics(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="metrics")
    checklist_total = models.PositiveIntegerField(default=0)
    checklist_done = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Métriques de {self.task}"
