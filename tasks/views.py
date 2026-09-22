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

# --- Cascade géographique (htmx) ---
from cities_light.models import City, Country, Region, SubRegion  # noqa: E402


@login_required
def geo_cascade(request):
    return render(request, "tasks/geo_cascade.html", {"countries": Country.objects.all()})


@login_required
def geo_regions(request):
    cid = request.GET.get("country")
    objs = Region.objects.filter(country_id=cid) if cid else Region.objects.none()
    return render(request, "tasks/partials/geo_options.html",
                  {"objects": objs, "placeholder": "— région / état —"})


@login_required
def geo_subregions(request):
    rid = request.GET.get("region")
    objs = SubRegion.objects.filter(region_id=rid) if rid else SubRegion.objects.none()
    return render(request, "tasks/partials/geo_options.html",
                  {"objects": objs, "placeholder": "— département / comté —"})


@login_required
def geo_cities(request):
    sid = request.GET.get("subregion")
    objs = City.objects.filter(subregion_id=sid) if sid else City.objects.none()
    return render(request, "tasks/partials/geo_options.html",
                  {"objects": objs, "placeholder": "— ville —"})


@login_required
def kanban(request, project_id):
    from .models import Project
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "tasks/kanban.html", {"project": project})


@login_required
def geo_advanced(request):
    return render(request, "tasks/geo_advanced.html", {})


# --- Démonstration des stratégies de cache (branche demo/cache) ---
from django.core.cache import cache  # noqa: E402
from django.views.decorators.cache import cache_page  # noqa: E402


def compute_dashboard_stats():
    """Agrégat « coûteux » : compté une fois puis mis en cache bas niveau."""
    from django.db.models import Count
    return {
        "tasks": Task.objects.count(),
        "projects": Project.objects.count(),
        "by_status": list(
            Status.objects.annotate(n=Count("tasks")).values("name", "n")
        ),
    }


@login_required
def dashboard(request):
    # 1) Cache bas niveau : l'agrégat coûteux est calculé une fois pour 5 min.
    stats = cache.get_or_set("dashboard_stats", compute_dashboard_stats, 300)
    # 2) Le fragment de template (dans dashboard.html) est mis en cache via {% cache %}.
    return render(request, "tasks/dashboard.html", {"stats": stats})


# 3) Cache de page entière, sur le cache dédié "pages" (Redis DB 2), 60 s.
@cache_page(60, cache="pages")
@login_required
def public_stats(request):
    stats = cache.get_or_set("dashboard_stats", compute_dashboard_stats, 300)
    return render(request, "tasks/dashboard.html", {"stats": stats})
