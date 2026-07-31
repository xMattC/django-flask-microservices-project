import requests
from django.conf import settings


class ProjectsServiceError(Exception):
    pass


class ProjectsServiceUnavailable(ProjectsServiceError):
    pass


def get_projects(user_id: int) -> list[dict]:
    """Retrieve all projects for a given user.

    Sends a GET request to the Projects service and returns the list of projects
    associated with the provided user ID.

    Parameters:
    - user_id : The ID of the authenticated user.

    Returns:
    - A list of project dictionaries.

    Raises:
    - ProjectsServiceUnavailable : If the Projects service cannot be reached.
    - ProjectsServiceError : If the service returns an error status, invalid JSON,
      or an unexpected response structure.
    """
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
    """Retrieve a single project for a given user.

    Sends a GET request to the Projects service and returns the project matching
    the provided project ID, ensuring it belongs to the given user.

    Parameters:
    - project_id : The ID of the project to retrieve.
    - user_id : The ID of the authenticated user.

    Returns:
    - A dictionary representing the project.

    Raises:
    - ProjectsServiceUnavailable : If the Projects service cannot be reached.
    - ProjectsServiceError : If the service returns an error status, invalid JSON,
      unexpected response structure, or an incorrect number of results.
    """
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


def create_project(user_id: int, payload: dict) -> dict:
    """Create a new project for a given user.

    Sends a POST request to the Projects service and returns the created project.

    Parameters:
    - user_id : The ID of the authenticated user.
    - payload : The data for the new project.

    Returns:
    - A dictionary representing the created project.

    Raises:
    - ProjectsServiceUnavailable : If the Projects service cannot be reached.
    - ProjectsServiceError : If the service returns an error status, invalid JSON,
      or an unexpected response structure.
    """
    url = f"{settings.PROJECTS_SERVICE_URL}/api/projects"

    try:
        response = requests.post(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)
    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code != 201:
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


def update_project(project_id: int, user_id: int, payload: dict) -> dict:
    """Update an existing project for a given user.

    Sends a PATCH request to the Projects service with the provided payload and
    returns the updated project.

    Parameters:
    - project_id : The ID of the project to update.
    - user_id : The ID of the authenticated user.
    - payload : A dictionary containing updated project data.

    Returns:
    - A dictionary representing the updated project.

    Raises:
    - ProjectsServiceUnavailable : If the Projects service cannot be reached.
    - ProjectsServiceError : If the service returns a non-200 status, invalid JSON,
      unexpected response structure, or an incorrect number of results.
    """
    url = f"{settings.PROJECTS_SERVICE_URL}/api/projects/{project_id}"

    try:
        response = requests.patch(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)
    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code != 200:
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


def delete_project(project_id: int, user_id: int) -> None:
    """Delete a project for a given user.

    Sends a DELETE request to the Projects service for the specified project.

    Parameters:
    - project_id : The ID of the project to delete.
    - user_id : The ID of the authenticated user.

    Returns:
    - None

    Raises:
    - ProjectsServiceUnavailable : If the Projects service cannot be reached.
    - ProjectsServiceError : If the service returns a non-204 status.
    """
    url = f"{settings.PROJECTS_SERVICE_URL}/api/projects/{project_id}"

    try:
        response = requests.delete(
            url,
            headers={"X-User-ID": str(user_id)},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise ProjectsServiceUnavailable("Projects service is unavailable.") from exc

    if response.status_code != 204:
        raise ProjectsServiceError(f"Projects service returned {response.status_code}")

