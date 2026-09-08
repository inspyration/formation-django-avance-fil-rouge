import pytest
from pytest_bdd import given, scenarios, then, when

from tasks.models import Task

pytestmark = pytest.mark.django_db
scenarios("features/task_status.feature")


@given("une tâche au statut initial", target_fixture="task")
def _(base):
    return Task.objects.create(name="T", project=base["project"], status=base["todo"])


@when("je passe la tâche à un statut final")
def _(task, base):
    task.status = base["done"]
    task.save()


@then("la date de fin réelle est renseignée")
def _(task):
    task.refresh_from_db()
    assert task.actual_end_datetime is not None
