# taskflow — application fil rouge (formation Django, Dawan)

Application de **suivi d'avancement de tâches**, support pédagogique construit
pas à pas. Django 6.1, PostgreSQL, front htmx + îlots Vue/Vite, API Django-Ninja.

> Application « propre » (bonnes pratiques), par contraste avec `auditflow`
> (l'application volontairement vulnérable auditée au jour 4).

## Démarrage rapide (dev, SQLite)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## Avec Docker (PostgreSQL)

```bash
docker compose up -d
```

## Convention de commits et de tags

Chaque **étape** et **sous-étape** de construction donne lieu à un commit et à un
tag numéroté `etape-X.Y` (X = phase, Y = sous-étape). Les **branches de démo**
partent du tag approprié et n'ajoutent que leur fonctionnalité, sans reprendre la
suite de `main`.

| Branche | Part du tag | Contenu |
|---------|-------------|---------|
| `main` | — | application complète |
| `demo/polymorphic` | (modèles + admin) | Task polymorphe + admin polymorphe |
| `demo/mptt` | (modèles + admin) | tâches / sous-tâches + admin MPTT |
| `demo/realtime` | (front Kanban) | Kanban temps réel (Django Channels) |
| `demo/modelisation-avancee` | (modèles) | champs non-naturels + enums avancés |
