"""Tâches Celery (branche demo/celery)."""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_project_created_email(project_id):
    """Prévient le propriétaire (owner) qu'un projet vient d'être créé."""
    from .models import Project

    project = Project.objects.select_related("owner").get(pk=project_id)
    owner = project.owner
    if not owner.email:
        return "owner sans e-mail, rien à envoyer"
    send_mail(
        subject=f"Projet créé : {project.name}",
        message=f"Bonjour {owner.get_username()},\n\n"
                f"Le projet « {project.name} » vient d'être créé.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner.email],
    )
    return f"e-mail envoyé à {owner.email}"
