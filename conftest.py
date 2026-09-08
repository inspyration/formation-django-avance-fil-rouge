import pytest


@pytest.fixture
def base(db):
    from django.contrib.auth.models import User
    from tasks.models import Project, Status
    user = User.objects.create_user("alice", "a@x.fr", "pw")
    project = Project.objects.create(name="P", owner=user)
    project.members.add(user)
    todo = Status.objects.create(name="À faire", order=0)
    done = Status.objects.create(name="Terminé", order=10, is_final=True)
    return {"user": user, "project": project, "todo": todo, "done": done}
