import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    client = APIClient()
    return client

#
# @pytest.fixture
# def default_users():
#     return User.objects.bulk_create(
#         [
#             User(
#                 username=f"김{team.label}",
#                 password=f"1234{team.value}",
#                 team=team,
#             )
#             for team in Team
#         ]
#     )
#
#
# @pytest.fixture
# def default_tasks(default_users):
#     return Task.objects.bulk_create(
#         [
#             Task(
#                 title=f"제목 by {user.username}",
#                 content=f"내용내용 by {user.username}",
#                 create_user_id=user.pk,
#                 team=user.team,
#             )
#             for user in default_users
#         ]
#     )
#
#
# @pytest.fixture
# def default_subtask(default_tasks):
#     def _default_subtask(create_user_id: int, team_name: str):
#         task = Task.objects.get(create_user_id=create_user_id)
#         sub_task = SubTask.objects.create(task_id=task.pk, team=team_name)
#         return sub_task
#
#     return _default_subtask
#
#
# @pytest.fixture
# def default_auth(default_users, api_client):
#     def _default_auth(user_id: int):
#         user = User.objects.get(pk=user_id)
#         api_client.force_login(user)
#         return user
#
#     return _default_auth
