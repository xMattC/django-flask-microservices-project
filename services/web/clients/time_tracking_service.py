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

    response = requests.post(url, json=payload, headers={"X-User-ID": str(user_id)}, timeout=5)

    data = response.json()

    return data["results"][0]