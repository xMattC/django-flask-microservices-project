import requests
from django.conf import settings


class TasksServiceError(Exception):
    """Base exception for Task service errors."""


class TasksServiceUnavailable(TasksServiceError):
    """Raised when the Task service cannot be reached."""


def _headers(user_id: int) -> dict[str, str]:
    """Build headers required by the Task service."""
    return {
        "X-User-ID": str(user_id),
    }


def _extract_results(response: requests.Response) -> list[dict]:
    """Validate and return the results list from a Task service response."""
    try:
        data = response.json()
    except ValueError as exc:
        raise TasksServiceError("Task service returned invalid JSON.") from exc

    try:
        results = data["results"]
    except KeyError as exc:
        raise TasksServiceError("Task service response missing results.") from exc

    if not isinstance(results, list):
        raise TasksServiceError("Task service results must be a list.")

    return results


def create_task(user_id: int, payload: dict) -> dict:
    """Create a task for the authenticated user."""
    url = f"{settings.TASK_SERVICE_URL}/api/tasks"

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_headers(user_id),
            timeout=5,
        )
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 201:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    results = _extract_results(response)

    if len(results) != 1:
        raise TasksServiceError("Task service must return exactly one created task.")

    return results[0]


def get_tasks(user_id: int, project_id: int | None = None) -> list[dict]:
    """Get tasks for the user, optionally filtered by project."""
    url = f"{settings.TASK_SERVICE_URL}/api/tasks"

    params = {}

    if project_id is not None:
        params["project_id"] = project_id

    try:
        response = requests.get(
            url,
            headers=_headers(user_id),
            params=params,
            timeout=5,
        )
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 200:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    return _extract_results(response)


def get_a_task(user_id: int, task_id: int) -> dict:
    """Get one task belonging to the authenticated user."""
    url = f"{settings.TASK_SERVICE_URL}/api/tasks/{task_id}"

    try:
        response = requests.get(
            url,
            headers=_headers(user_id),
            timeout=5,
        )
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 200:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    results = _extract_results(response)

    if len(results) != 1:
        raise TasksServiceError("Task service must return exactly one task.")

    return results[0]


def edit_a_task(user_id: int, task_id: int, payload: dict) -> dict:
    """Update a task belonging to the authenticated user."""
    url = f"{settings.TASK_SERVICE_URL}/api/tasks/{task_id}"

    try:
        response = requests.patch(
            url,
            json=payload,
            headers=_headers(user_id),
            timeout=5,
        )
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 200:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    results = _extract_results(response)

    if len(results) != 1:
        raise TasksServiceError("Task service must return exactly one task.")

    return results[0]


def delete_a_task(user_id: int, task_id: int) -> bool:
    """Delete a task belonging to the authenticated user."""
    url = f"{settings.TASK_SERVICE_URL}/api/tasks/{task_id}"

    try:
        response = requests.delete(
            url,
            headers=_headers(user_id),
            timeout=5,
        )
    except requests.RequestException as exc:
        raise TasksServiceUnavailable("Task service is unavailable.") from exc

    if response.status_code != 204:
        raise TasksServiceError(f"Task service returned {response.status_code}")

    return True
