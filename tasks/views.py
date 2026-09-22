from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .enums import Priority
from .forms import ChecklistFormSet, TaskForm
from .models import Project, Status, Task
from .pdf import render_task_pdf


@login_required
def task_pdf(request, pk):
    task = get_object_or_404(Task, pk=pk)
    pdf = render_task_pdf(task)
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="tache-{task.public_id}.pdf"'
    return resp


@login_required
def task_list(request):
    tasks = Task.objects.select_related("status", "project")
    return render(request, "tasks/task_list.html",
                  {"tasks": tasks, "statuses": Status.objects.all()})


@login_required
def task_search(request):
    q = request.GET.get("q", "")
    tasks = Task.objects.filter(name__icontains=q).select_related("status", "project")
    return render(request, "tasks/partials/task_rows.html",
                  {"tasks": tasks, "statuses": Status.objects.all()})


@login_required
def task_set_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST" and request.POST.get("status"):
        task.status_id = int(request.POST["status"])
        task.save()  # signal : fin réelle si statut final
    return render(request, "tasks/partials/task_row.html",
                  {"task": task, "statuses": Status.objects.all()})


@login_required
def assignees_options(request):
    pid = request.GET.get("project")
    users = User.objects.filter(member_projects__id=pid) if pid else User.objects.none()
    return render(request, "tasks/partials/assignees_options.html", {"users": users})


@login_required
def justification_field(request):
    show = request.GET.get("priority") == str(Priority.CRITICAL.value)
    return render(request, "tasks/partials/justification.html", {"show": show})


@login_required
def checklist_add_row(request):
    index = int(request.GET.get("index", 0))
    formset = ChecklistFormSet()
    form = formset.empty_form
    form.prefix = f"checklistitem_set-{index}"
    return render(request, "tasks/partials/checklist_row.html", {"form": form})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            formset = ChecklistFormSet(request.POST, instance=task)
            if formset.is_valid():
                formset.save()
            return redirect("tasks:task_list")
        formset = ChecklistFormSet(request.POST)
    else:
        form = TaskForm()
        formset = ChecklistFormSet()
    return render(request, "tasks/task_form.html", {"form": form, "formset": formset})


@login_required
def my_tasks(request):
    """Mes tâches ouvertes — réutilise TaskQuerySet.assigned_to().not_completed()."""
    tasks = (
        Task.objects.assigned_to(request.user)
        .not_completed()
        .select_related("status", "project")
    )
    return render(request, "tasks/my_tasks.html", {"tasks": tasks})


@login_required
def my_projects(request):
    """Mes projets avec au moins une tâche ouverte — ProjectQuerySet.with_unfinished_tasks_for()."""
    projects = Project.objects.with_unfinished_tasks_for(request.user)
    return render(request, "tasks/my_projects.html", {"projects": projects})
