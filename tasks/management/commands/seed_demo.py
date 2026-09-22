from datetime import timedelta

from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.enums import Priority, TaskKind
from tasks.models import (
    Assignment,
    ChecklistItem,
    Project,
    Status,
    Tag,
    Task,
    TaskMetrics,
)


class Command(BaseCommand):
    help = "Charge des données de démonstration (idempotent)."

    def handle(self, *args, **options):
        Task.objects.all().delete()
        Project.objects.all().delete()
        Status.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.filter(username__in=["alice", "bob", "charlie", "root"]).delete()

        statuses = {
            "todo": Status.objects.create(name="À faire", order=0, color="#9aa0a6"),
            "doing": Status.objects.create(name="En cours", order=10, color="#1a73e8"),
            "review": Status.objects.create(name="En revue", order=20, color="#f0a030"),
            "done": Status.objects.create(name="Terminé", order=30, is_final=True, color="#34a853"),
        }
        tags = {n: Tag.objects.create(name=n, slug=n) for n in ["backend", "frontend", "urgent", "doc"]}

        alice = User.objects.create_user(
            "alice", "alice@demo.example", "Password123",
            is_staff=True, first_name="Alice", last_name="Martin",
        )
        bob = User.objects.create_user(
            "bob", "bob@demo.example", "Password123",
            is_staff=True, first_name="Bob", last_name="Durand",
        )
        charlie = User.objects.create_user(
            "charlie", "charlie@demo.example", "Password123",
            is_staff=True, first_name="Charlie", last_name="Petit",
        )
        User.objects.create_superuser("root", "root@demo.example", "rootpwd")

        # Groupe « Team » : voir et modifier (pas supprimer) les objets métier.
        team_group, _ = Group.objects.get_or_create(name="Team")
        team_group.permissions.set(
            Permission.objects.filter(
                content_type__app_label="tasks",
                content_type__model__in=["task", "project", "checklistitem", "assignment"],
            ).filter(Q(codename__startswith="view_") | Q(codename__startswith="change_"))
        )
        # Rattache tous les comptes staff non-superadmin au groupe.
        for u in User.objects.filter(is_staff=True, is_superuser=False):
            u.groups.add(team_group)

        project = Project.objects.create(name="Refonte du site", slug="refonte-site", owner=alice)
        project.members.set([alice, bob, charlie])

        now = timezone.now()
        t1 = Task.objects.create(
            project=project, name="Maquette page d'accueil", status=statuses["doing"],
            priority=Priority.HIGH, task_kind=TaskKind.FEATURE.value, scrum_points=5,
            created_by=alice, target_datetime=now + timedelta(days=7),
            description="Concevoir la nouvelle page d'accueil.",
        )
        t1.tags.set([tags["frontend"], tags["urgent"]])
        Assignment.objects.create(task=t1, user=bob, role="contributor")
        for i, label in enumerate(["Wireframe", "Charte graphique", "Validation"]):
            ChecklistItem.objects.create(task=t1, label=label, order=i, done=(i == 0))

        t2 = Task.objects.create(
            project=project, name="Corriger le bug de connexion", status=statuses["done"],
            priority=Priority.CRITICAL, task_kind=TaskKind.BUG.value, scrum_points=3,
            created_by=bob, target_datetime=now - timedelta(days=3),
            actual_end_datetime=now - timedelta(days=1),  # terminé en retard -> delay > 0
            description="Erreur 500 sur le formulaire de login.",
        )
        Assignment.objects.create(task=t2, user=alice, role="reviewer")

        Task.objects.create(
            project=project, name="Mettre à jour la documentation", status=statuses["todo"],
            priority=Priority.LOW, task_kind=TaskKind.CHORE.value, scrum_points=2,
            created_by=charlie, description="Doc API à jour.",
        )

        for task in Task.objects.all():
            total = task.checklist.count()
            done = task.checklist.filter(done=True).count()
            TaskMetrics.objects.update_or_create(
                task=task, defaults={"checklist_total": total, "checklist_done": done}
            )

        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
        self.stdout.write("Comptes : alice / bob / charlie (Password123), root (rootpwd).")
        # Vérif du GeneratedField
        t2.refresh_from_db()
        self.stdout.write(f"Tâche '{t2.name}' — retard calculé (GeneratedField delay) : {t2.delay}")
