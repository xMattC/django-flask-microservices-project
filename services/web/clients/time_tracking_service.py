import requests
from django.conf import settings


class TimeTrackingServiceError(Exception):
    pass


class TimeTrackingServiceUnavailable(TimeTrackingServiceError):
    pass


def create_time_entries(user_id: int):
    """Create a new time entry for a given user."""
    pass