from typing import List

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

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
    return {"ok": True, "status_id": task.status_id, "actual_end": task.actual_end_datetime}
