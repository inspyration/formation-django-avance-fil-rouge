import pytest
from hamcrest import assert_that, equal_to

from tasks.models import Task
from tasks.pdf import render_task_pdf


@pytest.mark.django_db
def test_pdf_bytes(base):
    t = Task.objects.create(name="T", project=base["project"], status=base["todo"])
    assert_that(render_task_pdf(t)[:5], equal_to(b"%PDF-"))


@pytest.mark.django_db
def test_pdf_view(client, base):
    client.force_login(base["user"])
    t = Task.objects.create(name="T", project=base["project"], status=base["todo"])
    r = client.get(f"/tasks/{t.id}/pdf/")
    assert_that(r.status_code, equal_to(200))
    assert_that(r["Content-Type"], equal_to("application/pdf"))
