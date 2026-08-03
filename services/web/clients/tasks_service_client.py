import requests
from django.conf import settings


class TasksServiceError(Exception):
    pass


class TasksServiceUnavailable(TasksServiceError):
    pass

def create_task(user_id: int, payload: dict):
    """Create a new task entry for a given user.

    Sends a POST request to the Task service and returns the created task entry.

    Parameters:
    - user_id : The ID of the authenticated user.
    - payload : The data for the new task entry.

    Returns:
    - A dictionary representing the created task entry.
    """
    url = f"{settings.TASK_SERVICE_URL}/api/tasks"

    try:
        response = requests.post(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 201:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise TasksServiceError("Task service returned invalid JSON.") from exc

    if "results" not in data or not isinstance(data["results"], list):
        raise TasksServiceError("Task service returned invalid data structure.")

    data = response.json()

    return data["results"][0]

def get_tasks(user_id: int):
    url = f"{settings.TASK_SERVICE_URL}/api/tasks"
    response = requests.get(url, headers={"X-User-ID": str(user_id)}, timeout=5)
    data = response.json()

    return data["results"]


def get_a_task(user_id: int, task_id: int):
    pass

def edit_a_task(user_id: int, task_id: int):
    pass

def delete_a_task(user_id: int, task_id: int):
    pass