"""Administration avancée : visibilité métier et fieldsets sur-mesure.

Test autonome (django.test.TestCase) — la branche demo/admin-avance part de
etape-2.2, avant la mise en place de pytest (etape-7.1). Lancement :

    python manage.py test tasks.tests.test_admin_avance
"""
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from tasks.admin import FIELDSETS_STAFF, FIELDSETS_SUPERUSER, ProjectAdmin, TaskAdmin
from tasks.models import Assignment, Project, Status, Task


class AdminAvanceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.root = User.objects.create_superuser("root", "root@example.test", "x")
        cls.alice = User.objects.create_user("alice", is_staff=True)
        cls.bob = User.objects.create_user("bob", is_staff=True)
        cls.todo = Status.objects.create(name="À faire", order=1)

        # Projet d'Alice (elle en est membre) et projet de Bob (elle n'y est pas).
        cls.p_alice = Project.objects.create(name="Projet Alice", slug="projet-alice", owner=cls.root)
        cls.p_alice.members.add(cls.alice)
        cls.p_bob = Project.objects.create(name="Projet Bob", slug="projet-bob", owner=cls.root)
        cls.p_bob.members.add(cls.bob)

        # Tâches : une dans le projet d'Alice (visible), une affectée à Alice
        # dans le projet de Bob (visible), une purement chez Bob (cachée).
        cls.t_projet = Task.objects.create(name="dans-projet-alice",
                                           project=cls.p_alice, status=cls.todo)
        cls.t_affectee = Task.objects.create(name="affectee-alice",
                                             project=cls.p_bob, status=cls.todo)
        Assignment.objects.create(task=cls.t_affectee, user=cls.alice)
        cls.t_cachee = Task.objects.create(name="cachee-bob",
                                           project=cls.p_bob, status=cls.todo)

    def _req(self, user):
        req = self.factory.get("/")
        req.user = user
        return req

    def test_task_visibilite_membre(self):
        admin = TaskAdmin(Task, AdminSite())
        noms = set(admin.get_queryset(self._req(self.alice)).values_list("name", flat=True))
        self.assertEqual(noms, {"dans-projet-alice", "affectee-alice"})

    def test_task_visibilite_superuser(self):
        admin = TaskAdmin(Task, AdminSite())
        self.assertEqual(admin.get_queryset(self._req(self.root)).count(), 3)

    def test_project_visibilite_membre(self):
        admin = ProjectAdmin(Project, AdminSite())
        noms = set(admin.get_queryset(self._req(self.alice)).values_list("name", flat=True))
        self.assertEqual(noms, {"Projet Alice"})

    def test_fieldsets_sur_mesure(self):
        admin = TaskAdmin(Task, AdminSite())
        self.assertEqual(admin.get_fieldsets(self._req(self.alice)), FIELDSETS_STAFF)
        self.assertEqual(admin.get_fieldsets(self._req(self.root)), FIELDSETS_SUPERUSER)

    def test_fieldsets_plusieurs_champs_par_ligne(self):
        # Au moins une ligne regroupe plusieurs champs (tuple imbriqué).
        rows = [r for _, opts in FIELDSETS_STAFF for r in opts["fields"]]
        self.assertTrue(any(isinstance(r, tuple) and len(r) > 1 for r in rows))
