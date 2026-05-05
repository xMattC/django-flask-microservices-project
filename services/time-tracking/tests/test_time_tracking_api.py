from app.models import TimeEntry

USER_HEADERS = {"X-User-ID": "123"}


def get_response_data(response):
    """Return JSON response data."""
    return response.get_json()


def get_first_result(response):
    """Return the first item from a results response."""
    return get_response_data(response)["results"][0]


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY CREATE TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_create_time_entry_success(app, client):
    payload = {
        "project_id": 1,
        "description": "Initial work session",
    }
    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_data = get_first_result(response)

    assert entry_data["id"] is not None
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["description"] == payload["description"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]

    assert entry_data["started_at"] is not None
    assert entry_data["ended_at"] is None
    assert entry_data["duration_seconds"] is None

    with app.app_context():
        entry = TimeEntry.query.filter_by(owner_user_id=USER_HEADERS["X-User-ID"]).first()

    assert entry is not None
    assert entry.project_id == payload["project_id"]
    assert entry.description == payload["description"]
    assert entry.ended_at is None

