import requests
from django.conf import settings


class ProjectsServiceError(Exception):
    pass


class ProjectsServiceUnavailable(ProjectsServiceError):
    pass


def get_projects(user_id: int) -> list[dict]:
    url = f"{settings.PROJECTS_SERVICE_URL}/projects"

    try:
        response = requests.get(
            url,
            headers={"X-User-ID": str(user_id)},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code >= 400:
        raise ProjectsServiceError(f"Projects service returned {response.status_code}")

    data = response.json()
    return data.get("results", [])