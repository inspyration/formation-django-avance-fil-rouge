from typing import List

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ninja.security import django_auth

from cities_light.models import City

from .models import Status, Task

api = NinjaAPI(title="taskflow API", auth=django_auth)


class StatusOut(Schema):
    id: int
    name: str
    color: str
    order: int
    is_final: bool


class TaskCard(Schema):
    id: int
    name: str
    status_id: int
    priority: int
    assignees: List[str]


class BoardOut(Schema):
    statuses: List[StatusOut]
    tasks: List[TaskCard]


class MoveIn(Schema):
    status_id: int


@api.get("/projects/{project_id}/board", response=BoardOut)
def board(request, project_id: int):
    statuses = list(Status.objects.all())
    tasks = (
        Task.objects.filter(project_id=project_id)
        .select_related("status")
        .prefetch_related("assignees")
    )
    cards = [
        TaskCard(
            id=t.id, name=t.name, status_id=t.status_id, priority=t.priority,
            assignees=[u.username for u in t.assignees.all()],
        )
        for t in tasks
    ]
    return {"statuses": statuses, "tasks": cards}


@api.post("/tasks/{task_id}/move")
def move(request, task_id: int, payload: MoveIn):
    task = get_object_or_404(Task, pk=task_id)
    task.status_id = payload.status_id
    task.save()  # déclenche le signal (fin réelle si statut final)
    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(
            f"board_{task.project_id}",
            {"type": "board.update", "task_id": task.id, "status_id": task.status_id},
        )
    return {"ok": True, "status_id": task.status_id, "actual_end": task.actual_end_datetime}


class CityOut(Schema):
    id: int
    label: str


@api.get("/cities", response=List[CityOut])
def city_search(request, q: str = "", subregion: int | None = None, limit: int = 20):
    """Autocomplétion ville côté serveur (gros volume) : filtrée et bornée.
    S'appuie sur l'index nom de cities-light ; jamais de <select> géant côté client."""
    qs = City.objects.select_related("subregion", "country")
    if subregion:
        qs = qs.filter(subregion_id=subregion)
    if q:
        qs = qs.filter(name__icontains=q)
    qs = qs.order_by("name")[: min(limit, 50)]
    return [
        CityOut(id=c.id, label=f"{c.name} ({c.subregion.name if c.subregion_id else '-'}, {c.country.code2})")
        for c in qs
    ]
