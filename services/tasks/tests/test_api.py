from app.models import Tasks

USER_HEADERS = {"X-User-ID": "123"}
OTHER_USER_HEADERS = {"X-User-ID": "999"}


def get_response_data(response):
    """Return JSON response data."""
    return response.get_json()


def get_first_result(response):
    """Return the first item from a results response."""
    return get_response_data(response)["results"][0]


# ---------------------------------------------------------------------------------------------------------------------
# TASK CREATE TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_create_task_success(app, client):
    payload = {
        "project_id": 1,
        "task_name": "Initial task",
        "description": "Initial work session",
    }
    response = client.post("/api/task", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_data = get_first_result(response)

    assert entry_data["id"] is not None
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["description"] == payload["description"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]

    assert entry_data["started_at"] is not None
    assert entry_data["ended_at"] is None

    with app.app_context():
        entry = Tasks.query.filter_by(owner_user_id=USER_HEADERS["X-User-ID"]).first()

    assert entry is not None
    assert entry.project_id == payload["project_id"]
    assert entry.description == payload["description"]
    assert entry.ended_at is None


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY READ (LIST) TESTS
# --------------------------------------------------------------------------------------------------------------------


def test_get_all_time_entries(client):
    pass


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY READ (DETAIL) TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_get_task_detail_success(client):
    pass


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY UPDATE TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_update_task_success(client):
    pass


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY DELETE TESTS
# ---------------------------------------------------------------------------------------------------------------------
def test_delete_task_success(client):
    pass
