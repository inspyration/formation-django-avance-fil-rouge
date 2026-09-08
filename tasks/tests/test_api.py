import pytest
from hamcrest import assert_that, equal_to, greater_than_or_equal_to

from tasks.models import Task


@pytest.mark.django_db
def test_board(client, base):
    client.force_login(base["user"])
    Task.objects.create(name="T", project=base["project"], status=base["todo"])
    r = client.get(f"/api/projects/{base['project'].id}/board")
    assert_that(r.status_code, equal_to(200))
    data = r.json()
    assert_that(len(data["statuses"]), greater_than_or_equal_to(2))
    assert_that(len(data["tasks"]), greater_than_or_equal_to(1))
