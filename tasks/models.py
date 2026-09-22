import uuid

from django.conf import settings
from django.db import models

from .enums import Priority, TaskKind, task_kind_choices
from .mixins import OrderingMixin, TrackingMixin


# --- Managers & QuerySets (step 2.4: three approaches) ---


class ProjectQuerySet(models.QuerySet):
    """QuerySet exposed directly via as_manager() (approach 1)."""

    def with_unfinished_tasks_for(self, user):
        """Projects where the user is assigned to at least one open task."""
        return self.filter(
            tasks__assignees=user, tasks__status__is_final=False
        ).distinct()

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class TaskQuerySet(models.QuerySet):
    """Business queryset, chained composably."""

    def assigned_to(self, user):
        return self.filter(assignees=user)

    def not_completed(self):
        return self.filter(status__is_final=False)

    def for_project(self, project):
        return self.filter(project=project)

    def get_by_natural_key(self, public_id):
        return self.get(public_id=public_id)


class TaskManager(models.Manager.from_queryset(TaskQuerySet)):
    """Manager built from the queryset (approach 2): may add manager-only methods."""

    def open_count(self):
        return self.not_completed().count()


class StatusManager(models.Manager):
    """Plain custom Manager, no dedicated QuerySet class (approach 3)."""

    def get_by_natural_key(self, name):
        return self.get(name=name)

    def finals(self):
        return self.get_queryset().filter(is_final=True)



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

    objects = ProjectQuerySet.as_manager()

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return self.name


class Status(OrderingMixin):
    name = models.CharField(max_length=100)
    is_final = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default="#888888")

    objects = StatusManager()

    def natural_key(self):
        return (self.name,)

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
    is_billable = models.BooleanField(default=False)
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

    objects = TaskManager()

    class Meta:
        ordering = ["-created_at"]

    def natural_key(self):
        return (str(self.public_id),)

    def __str__(self):
        return self.name

    def duplicate(self):
        """Duplicate the task, keeping a link to the original (no re-opening)."""
        clone = Task.objects.create(
            name=f"{self.name} (copie)",
            description=self.description,
            priority=self.priority,
            task_kind=self.task_kind,
            scrum_points=self.scrum_points,
            estimated_cost=self.estimated_cost,
            estimated_duration=self.estimated_duration,
            target_datetime=self.target_datetime,
            status=self.status,
            project=self.project,
            created_by=self.created_by,
            original_task=self,
            is_billable=self.is_billable,
            reference_url=self.reference_url,
            metadata=dict(self.metadata),
        )
        clone.tags.set(self.tags.all())
        for item in self.checklist.all():
            ChecklistItem.objects.create(task=clone, label=item.label, order=item.order)
        return clone


class Assignment(models.Model):
    ROLES = [
        ("owner", "Responsable"),
        ("contributor", "Contributeur"),
        ("reviewer", "Relecteur"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default="contributor")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task", "user"], name="unique_assignment")
        ]

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
