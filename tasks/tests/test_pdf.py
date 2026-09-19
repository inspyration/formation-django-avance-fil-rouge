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


@pytest.mark.django_db
def test_pdf_emailed(base, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    from django.core import mail

    from tasks.tasks import generate_task_pdf
    t = Task.objects.create(
        name="T", project=base["project"], status=base["todo"], reporter_email="qa@x.test"
    )
    generate_task_pdf.enqueue(t.id)  # backend immediate -> exécution synchrone
    assert_that(len(mail.outbox), equal_to(1))
    assert_that(len(mail.outbox[0].attachments), equal_to(1))
