from django.contrib.auth import get_user_model
from django.core import serializers
from django.test import TestCase

from tasks.models import Assignment, Project, Status, Task

User = get_user_model()


class ManagerAndNaturalKeyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user("alice")
        cls.bob = User.objects.create_user("bob")
        cls.todo = Status.objects.create(name="Todo", order=0)
        cls.done = Status.objects.create(name="Done", order=10, is_final=True)
        cls.project = Project.objects.create(name="P1", slug="p1", owner=cls.alice)
        cls.t_open = Task.objects.create(
            name="Open", project=cls.project, status=cls.todo, created_by=cls.alice
        )
        cls.t_done = Task.objects.create(
            name="Done", project=cls.project, status=cls.done, created_by=cls.alice
        )
        Assignment.objects.create(task=cls.t_open, user=cls.bob, role="contributor")
        Assignment.objects.create(task=cls.t_done, user=cls.bob, role="contributor")

    def test_business_methods_chain(self):
        qs = Task.objects.assigned_to(self.bob).not_completed()
        self.assertEqual(list(qs), [self.t_open])
        with self.assertNumQueries(1):
            list(Task.objects.assigned_to(self.bob).not_completed())

    def test_manager_only_method(self):
        self.assertEqual(Task.objects.open_count(), 1)

    def test_project_with_unfinished_tasks_for(self):
        self.assertEqual(
            list(Project.objects.with_unfinished_tasks_for(self.bob)), [self.project]
        )

    def test_status_manager_finals(self):
        self.assertEqual(list(Status.objects.finals()), [self.done])

    def test_natural_key_roundtrip(self):
        data = serializers.serialize(
            "json", [self.t_open],
            use_natural_primary_keys=True, use_natural_foreign_keys=True,
        )
        self.assertIn('"p1"', data)     # FK projet sérialisée par slug
        self.assertIn('"Todo"', data)   # FK statut sérialisée par name
        self.assertEqual(Project.objects.get_by_natural_key("p1"), self.project)
        self.assertEqual(Status.objects.get_by_natural_key("Todo"), self.todo)
        self.assertEqual(
            Task.objects.get_by_natural_key(str(self.t_open.public_id)), self.t_open
        )
