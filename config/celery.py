"""Application Celery du projet (démonstration isolée — branche demo/celery).

Le fil rouge (main) utilise les tâches natives de Django 6 (django.tasks) pour le
travail de fond. Cette branche montre l'alternative « classique » : Celery avec
un broker Redis. Lancer un worker :

    celery -A config worker -l info
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("taskflow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
