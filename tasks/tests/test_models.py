import pytest
from hamcrest import assert_that, equal_to, is_not, none, starts_with

from tasks.models import ChecklistItem, Task


@pytest.mark.django_db
def test_slug_auto(base):
    t = Task.objects.create(name="Ma tâche", project=base["project"], status=base["todo"])
    assert_that(t.slug, equal_to("ma-tache"))


@pytest.mark.django_db
def test_actual_end_write_once(base):
    t = Task.objects.create(name="T", project=base["project"], status=base["todo"])
    assert_that(t.actual_end_datetime, none())
    t.status = base["done"]; t.save(); t.refresh_from_db()
    assert_that(t.actual_end_datetime, is_not(none()))


@pytest.mark.django_db
def test_metrics_signal(base):
    t = Task.objects.create(name="T", project=base["project"], status=base["todo"])
    ChecklistItem.objects.create(task=t, label="a")
    ChecklistItem.objects.create(task=t, label="b", done=True)
    t.refresh_from_db()
    assert_that(t.metrics.checklist_total, equal_to(2))
    assert_that(t.metrics.checklist_done, equal_to(1))


@pytest.mark.django_db
def test_duplicate(base):
    t = Task.objects.create(name="Orig", project=base["project"], status=base["todo"])
    ChecklistItem.objects.create(task=t, label="x")
    clone = t.duplicate()
    assert_that(clone.original_task_id, equal_to(t.id))
    assert_that(clone.name, starts_with("Orig"))
    assert_that(clone.checklist.count(), equal_to(1))
