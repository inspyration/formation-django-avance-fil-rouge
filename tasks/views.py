from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Task
from .pdf import render_task_pdf


@login_required
def task_pdf(request, pk):
    task = get_object_or_404(Task, pk=pk)
    pdf = render_task_pdf(task)
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="tache-{task.public_id}.pdf"'
    return resp
