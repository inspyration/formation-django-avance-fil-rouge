"""Signaux du domaine.

À présenter en formation avec leurs **limites** : les signaux se déclenchent sur
`Model.save()` / `delete()`, mais **pas** sur `QuerySet.update()` ni
`bulk_create()`/`bulk_update()`. Pour une logique critique, préférer une méthode
de service ou une transition d'état explicite.
"""
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from .models import ChecklistItem, Project, Tag, Task, TaskMetrics
from .celery_tasks import send_project_created_email


@receiver(pre_save, sender=Task)
def task_set_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)[:270]


@receiver(pre_save, sender=Project)
def project_set_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)[:220]


@receiver(pre_save, sender=Tag)
def tag_set_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)[:90]


@receiver(pre_save, sender=Task)
def task_mark_end_when_final(sender, instance, **kwargs):
    """Horodate la fin réelle (write-once) quand la tâche passe à un statut final."""
    if instance.status_id and instance.actual_end_datetime is None:
        if instance.status.is_final:
            instance.actual_end_datetime = timezone.now()


@receiver(post_save, sender=ChecklistItem)
@receiver(post_delete, sender=ChecklistItem)
def refresh_task_metrics(sender, instance, **kwargs):
    task = instance.task
    metrics, _ = TaskMetrics.objects.get_or_create(task=task)
    metrics.checklist_total = task.checklist.count()
    metrics.checklist_done = task.checklist.filter(done=True).count()
    metrics.save()


@receiver(post_save, sender=Project)
def project_created_notify_owner(sender, instance, created, **kwargs):
    """À la création d'un projet, envoie un e-mail au owner via Celery (asynchrone)."""
    if created:
        send_project_created_email.delay(instance.pk)
