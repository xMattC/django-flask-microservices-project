import requests
from django.conf import settings


class TimeTrackingServiceError(Exception):
    pass


class TimeTrackingServiceUnavailable(TimeTrackingServiceError):
    pass


def create_time_entry(user_id: int, payload: dict):
    """Create a new time entry for a given user.

    Sends a POST request to the Time Tracking service and returns the created time entry.

    Parameters:
    - user_id : The ID of the authenticated user.
    - payload : The data for the new time entry.

    Returns:
    - A dictionary representing the created time entry.
    """
    url = f"{settings.TIME_TRACKING_SERVICE_URL}/api/time-entries"

    try:
        response = requests.post(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)
    except requests.RequestException as exc:
        raise TimeTrackingServiceUnavailable("Time tracking service is unavailable.") from exc

    if response.status_code != 201:
        raise TimeTrackingServiceError(f"Time tracking service returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise TimeTrackingServiceError("Time tracking service returned invalid JSON.") from exc

    if "results" not in data or not isinstance(data["results"], list):
        raise TimeTrackingServiceError("Time tracking service returned invalid data structure.")

    return data["results"][0]


def get_time_entries(user_id: int, project_id: int | None = None, running_only: bool = False):
    """Get time entries for a given user, optionally filtered by project and running status.

    Sends a GET request to the Time Tracking service and returns a list of time entries.

    Parameters:
    - user_id : The ID of the authenticated user.
    - project_id : Optional project ID filter.
    - running_only : If True, only running time entries are returned.

    Returns:
    - A list of dictionaries representing the time entries.
    """
    url = f"{settings.TIME_TRACKING_SERVICE_URL}/api/time-entries"

    params = {}

    if project_id is not None:
        params["project_id"] = project_id

    if running_only:
        params["running_only"] = "true"

    try:
        response = requests.get(url, headers={"X-User-ID": str(user_id)}, params=params, timeout=5)
    except requests.RequestException as exc:
        raise TimeTrackingServiceUnavailable("Time tracking service is unavailable.") from exc

    if response.status_code != 200:
        raise TimeTrackingServiceError(f"Time tracking service returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise TimeTrackingServiceError("Time tracking service returned invalid JSON.") from exc

    try:
        results = data["results"]
    except KeyError as exc:
        raise TimeTrackingServiceError("Time tracking service response missing results.") from exc

    if not isinstance(results, list):
        raise TimeTrackingServiceError("Time tracking service results must be a list.")

    return results


def get_time_entry(user_id: int, time_entry_id: int):
    """Get a single time entry for a given user.

    Sends a GET request to the Time Tracking service and returns one time entry.

    Parameters:
    - user_id : The ID of the authenticated user.
    - time_entry_id : The ID of the time entry to retrieve.

    Returns:
    - A dictionary representing the time entry.
    """

    url = f"{settings.TIME_TRACKING_SERVICE_URL}/api/time-entries/{time_entry_id}"

    try:
        response = requests.get(url, headers={"X-User-ID": str(user_id)}, timeout=5)
    except requests.RequestException as exc:
        raise TimeTrackingServiceUnavailable("Time tracking service is unavailable.") from exc

    if response.status_code != 200:
        raise TimeTrackingServiceError(f"Time tracking service returned {response.status_code}")

    data = response.json()

    try:
        results = data["results"]
    except KeyError as exc:
        raise TimeTrackingServiceError("Time tracking service response missing results.") from exc

    if not isinstance(results, list):
        raise TimeTrackingServiceError("Time tracking service results must be a list.")

    if len(results) != 1:
        raise TimeTrackingServiceError("Time tracking service must return exactly one time entry.")

    return results[0]

def stop_time_entry(user_id: int, time_entry_id: int):
    """Stop a running time entry for a given user.

    Sends a POST request to the Time Tracking service and returns the stopped time entry.

    Parameters:
    - user_id : The ID of the authenticated user.
    - time_entry_id : The ID of the time entry to stop.

    Returns:
    - A dictionary representing the stopped time entry.
    """
    url = f"{settings.TIME_TRACKING_SERVICE_URL}/api/time-entries/{time_entry_id}/stop"

    response = requests.post(url, headers={"X-User-ID": str(user_id)}, timeout=5)

    data = response.json()

    return data["results"][0]