import requests
from django.conf import settings


class TaskServiceError(Exception):
    pass


class TaskServiceUnavailable(TaskServiceError):
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

    response = requests.post(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)

    data = response.json()

    return data["results"][0]

def get_tasks(user_id: int):
    pass

def get_a_task(user_id: int, task_id: int):
    pass

def edit_a_task(user_id: int, task_id: int):
    pass

def delete_a_task(user_id: int, task_id: int):
    pass