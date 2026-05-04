import requests
from django.conf import settings


class ProjectsServiceError(Exception):
    pass


class ProjectsServiceUnavailable(ProjectsServiceError):
    pass


def get_projects(user_id: int) -> list[dict]:
    url = f"{settings.PROJECTS_SERVICE_URL}/api/projects"

    try:
        response = requests.get(url, headers={"X-User-ID": str(user_id)}, timeout=5)

    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code >= 400:
        raise ProjectsServiceError(f"Projects service returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise ProjectsServiceError("Projects service returned invalid JSON.") from exc

    if "results" not in data or not isinstance(data["results"], list):
        raise ProjectsServiceError("Projects service returned invalid data structure.")

    return data["results"]

def get_project(project_id: int, user_id: int) -> dict:
    url = f"{settings.PROJECTS_SERVICE_URL}/api/projects/{project_id}"

    try:
        response = requests.get(url, headers={"X-User-ID": str(user_id)}, timeout=5)

    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code >= 400:
        raise ProjectsServiceError(f"Projects service returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise ProjectsServiceError("Projects service returned invalid JSON.") from exc

    if "results" not in data or not isinstance(data["results"], list):
        raise ProjectsServiceError("Projects service returned invalid data structure.")

    if len(data["results"]) != 1:
        raise ProjectsServiceError("Projects service returned invalid project result.")

    return data["results"][0]