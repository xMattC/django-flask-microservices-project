import os
import uuid

import pytest
import requests


PROJECTS_URL = os.getenv("PROJECTS_SERVICE_URL", "http://localhost:5000/api")
TIME_TRACKING_URL = os.getenv("TIME_TRACKING_SERVICE_URL", "http://localhost:5001/api")


@pytest.fixture
def user_a():
    return f"e2e-user-a-{uuid.uuid4()}"


@pytest.fixture
def user_b():
    return f"e2e-user-b-{uuid.uuid4()}"


@pytest.fixture
def projects_client():
    return ServiceClient(PROJECTS_URL)


@pytest.fixture
def time_tracking_client():
    return ServiceClient(TIME_TRACKING_URL)


class ServiceClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def request(self, method, path, user_id=None, **kwargs):
        headers = kwargs.pop("headers", {})
        if user_id is not None:
            headers["X-User-ID"] = user_id

        return requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            headers=headers,
            timeout=10,
            **kwargs,
        )

    def get(self, path, user_id=None, **kwargs):
        return self.request("GET", path, user_id=user_id, **kwargs)

    def post(self, path, user_id=None, **kwargs):
        return self.request("POST", path, user_id=user_id, **kwargs)

    def patch(self, path, user_id=None, **kwargs):
        return self.request("PATCH", path, user_id=user_id, **kwargs)

    def delete(self, path, user_id=None, **kwargs):
        return self.request("DELETE", path, user_id=user_id, **kwargs)