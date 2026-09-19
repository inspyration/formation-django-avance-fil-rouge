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

## Développement local (services via Docker, Django sur l'hôte)

Django s'installe et se lance **en local** ; Docker ne fournit que les services :
**PostgreSQL 18**, **Mailpit** (SMTP de dev + interface web), **Redis**
(+ **RedisInsight**, son visualiseur web), **Adminer**.

```bash
docker compose up -d          # postgres / mailpit / redis / adminer / redisinsight
cp .env.example .env          # DB_ENGINE=postgres, e-mail vers Mailpit
python manage.py migrate && python manage.py seed_demo && python manage.py seed_geo
python manage.py runserver
```

- Mailpit (e-mails capturés, dont la fiche PDF envoyée en tâche de fond) : http://localhost:8025
- Adminer (inspection de la base) : http://localhost:8080
- RedisInsight (visualisation du cache Redis) : http://localhost:5540

> Procédure d'installation détaillée et guide des interfaces (Mailpit, Adminer,
> RedisInsight) : voir le PDF *Environnement de développement local* fourni par le formateur.

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

## Notes techniques

- **`delay` (GeneratedField)** a une **sémantique PostgreSQL** (soustraction
  date/heure) : sous SQLite (dev rapide) il vaut `0`. Utiliser PostgreSQL (docker)
  pour la valeur exacte. Bon exemple de fonctionnalité spécifique au moteur.
- **Front Vue** : `cd frontend && npm install && npm run build` (servi via
  django-vite en mode manifest). Dev avec HMR : `VITE_DEV=true` + `npm run dev`.
- **Géo** : `manage.py seed_geo` (petit jeu FR/US pour la démo) ; pour le volume
  réel (autocomplétion sur gros dataset) : `manage.py cities_light` (téléchargement
  geonames, restreint à FR+US par les settings).
- **Tests** : `pytest` (SQLite).

## Branches de démonstration

Chacune part d'un tag et n'ajoute que sa fonctionnalité (sans la suite de main) :

| Branche | Tag de départ | Ajoute | Runtime |
|---------|---------------|--------|---------|
| `demo/polymorphic` | `etape-2.2` | Task polymorphe + admin polymorphe | — |
| `demo/mptt` | `etape-2.2` | arbre tâches/sous-tâches + admin MPTT | — |
| `demo/modelisation-avancee` | `etape-2.1` | enums riches + champs supplémentaires | ArrayField/DateRange = PostgreSQL |
| `demo/realtime` | `etape-5.3` | Kanban temps réel (Channels) | serveur ASGI (daphne/uvicorn) |
