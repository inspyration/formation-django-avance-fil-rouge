"""Enums avancés (enum-properties + django-enum).

- enum-properties : chaque membre porte des propriétés (label, couleur…).
- django-enum : EnumField branche ces enums comme champ de modèle (contrainte
  en base, formulaires, filtres).
"""
from enum_properties import IntEnumProperties, StrEnumProperties


class Severity(IntEnumProperties):
    label: str
    color: str

    LOW = 1, "Basse", "#9aa0a6"
    MEDIUM = 2, "Moyenne", "#1a73e8"
    HIGH = 3, "Haute", "#f0a030"
    CRITICAL = 4, "Critique", "#d93025"


class RiskLevel(StrEnumProperties):
    label: str

    LOW = "low", "Faible"
    MEDIUM = "medium", "Modéré"
    HIGH = "high", "Élevé"
