"""Tâches de fond — cadre natif de Django 6.0 (django.tasks).

En dev : backend « immediate » (exécution synchrone). En production, on
brancherait un backend avec worker. Illustre la nouveauté 6.0 sans celery.
"""
from pathlib import Path

from django.conf import settings
from django.tasks import task


@task
def generate_task_pdf(task_id: int) -> str:
    from .models import Task
    from .pdf import render_task_pdf

    task_obj = Task.objects.get(pk=task_id)
    pdf = render_task_pdf(task_obj)
    out_dir = Path(settings.MEDIA_ROOT) / "fiches"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"tache-{task_obj.public_id}.pdf"
    out_path.write_bytes(pdf)
    return str(out_path)
