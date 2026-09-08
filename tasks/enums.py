from enum import StrEnum

from django.db import models


class Priority(models.IntegerChoices):
    LOW = 10, "Basse"
    MEDIUM = 20, "Moyenne"
    HIGH = 30, "Haute"
    CRITICAL = 40, "Critique"


class TaskKind(StrEnum):
    """Enum standard (PEP 435) — illustre l'usage d'un StrEnum avec Django."""
    FEATURE = "feature"
    BUG = "bug"
    CHORE = "chore"


def task_kind_choices():
    return [(k.value, k.name.capitalize()) for k in TaskKind]
