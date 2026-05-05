from datetime import datetime, timezone

from app.models import TimeEntry
from app.extensions import db

USER_HEADERS = {"X-User-ID": "123"}
OTHER_USER_HEADERS = {"X-User-ID": "999"}


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


def test_create_time_entry_missing_user_header(client):
    payload = {
        "project_id": 1,
        "description": "Initial work session",
    }

    response = client.post("/api/time-entries", json=payload)

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing X-User-ID header"


def test_create_time_entry_missing_project_id(client):
    payload = {
        "description": "Initial work session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 422
    assert "errors" in response.get_json()


def test_create_time_entry_null_project_id(client):
    payload = {
        "project_id": None,
        "description": "Initial work session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 422
    assert "errors" in response.get_json()


def test_create_time_entry_optional_description(client):
    payload = {
        "project_id": 1,
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_data = get_first_result(response)

    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["description"] is None


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY READ (LIST) TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_get_time_entries_returns_empty_list(client):
    response = client.get("/api/time-entries", headers=USER_HEADERS)

    assert response.status_code == 200

    data = get_response_data(response)

    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0


def test_get_all_time_entries(client):
    payload_1 = {"project_id": 1, "description": "Initial work session"}
    payload_2 = {"project_id": 2, "description": "Second work session"}

    client.post("/api/time-entries", json=payload_1, headers=USER_HEADERS)
    client.post("/api/time-entries", json=payload_2, headers=USER_HEADERS)

    response = client.get("/api/time-entries", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]
    descriptions = [entry["description"] for entry in entries]

    assert len(entries) == 2
    assert payload_1["description"] in descriptions
    assert payload_2["description"] in descriptions


def test_get_time_entries_limited_to_user(client):
    other_user_payload = {"project_id": 1, "description": "Other user session"}
    current_user_payload = {"project_id": 1, "description": "Current user session"}

    client.post("/api/time-entries", json=other_user_payload, headers=OTHER_USER_HEADERS)
    client.post("/api/time-entries", json=current_user_payload, headers=USER_HEADERS)

    response = client.get("/api/time-entries", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]

    assert len(entries) == 1
    assert entries[0]["description"] == current_user_payload["description"]


def test_get_time_entries_missing_user_header(client):
    response = client.get("/api/time-entries")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing X-User-ID header"


def test_get_time_entries_filtered_by_project_id(client):
    payload_1 = {"project_id": 1, "description": "Project one session"}
    payload_2 = {"project_id": 2, "description": "Project two session"}

    client.post("/api/time-entries", json=payload_1, headers=USER_HEADERS)
    client.post("/api/time-entries", json=payload_2, headers=USER_HEADERS)

    response = client.get("/api/time-entries?project_id=2", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]

    assert len(entries) == 1
    assert entries[0]["project_id"] == 2
    assert entries[0]["description"] == payload_2["description"]


def test_get_time_entries_filtered_by_running_only(app, client):
    running_payload = {"project_id": 1, "description": "Running session"}
    stopped_payload = {"project_id": 1, "description": "Stopped session"}

    running_response = client.post("/api/time-entries", json=running_payload, headers=USER_HEADERS)
    stopped_response = client.post("/api/time-entries", json=stopped_payload, headers=USER_HEADERS)

    stopped_entry_id = get_first_result(stopped_response)["id"]

    with app.app_context():
        stopped_entry = TimeEntry.query.get(stopped_entry_id)
        stopped_entry.ended_at = datetime.now(timezone.utc)
        db.session.commit()

    response = client.get("/api/time-entries?running_only=true", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]

    assert len(entries) == 1
    assert entries[0]["id"] == get_first_result(running_response)["id"]
    assert entries[0]["ended_at"] is None


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY READ (DETAIL) TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_get_time_entry_detail_success(client):
    payload = {
        "project_id": 1,
        "description": "Detail work session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.get(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert response.status_code == 200

    entry_data = get_first_result(response)

    assert entry_data["id"] == entry_id
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["description"] == payload["description"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]
    assert entry_data["started_at"] is not None
    assert entry_data["ended_at"] is None


def test_get_time_entry_detail_not_found(client):
    response = client.get("/api/time-entries/999", headers=USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_get_time_entry_detail_other_user_returns_404(client):
    payload = {
        "project_id": 1,
        "description": "Other user detail test",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.get(f"/api/time-entries/{entry_id}", headers=OTHER_USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_get_time_entry_detail_missing_user_header(client):
    response = client.get("/api/time-entries/1")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing X-User-ID header"


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY STOP TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_stop_time_entry_success(client):
    payload = {
        "project_id": 1,
        "description": "Stop test session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    assert response.status_code == 200

    entry_data = get_first_result(response)

    assert entry_data["id"] == entry_id
    assert entry_data["ended_at"] is not None
    assert entry_data["duration_seconds"] is not None


def test_stop_time_entry_already_stopped(client):
    payload = {
        "project_id": 1,
        "description": "Already stopped session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    assert response.status_code == 200

    first_ended_at = get_first_result(response)["ended_at"]

    response = client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    assert response.status_code == 200

    entry_data = get_first_result(response)

    assert entry_data["ended_at"] == first_ended_at
    assert entry_data["duration_seconds"] is not None


def test_stop_time_entry_not_found(client):
    response = client.patch("/api/time-entries/999/stop", headers=USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_stop_time_entry_other_user_returns_404(client):
    payload = {
        "project_id": 1,
        "description": "Other user stop test",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.patch(f"/api/time-entries/{entry_id}/stop", headers=OTHER_USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_stop_time_entry_missing_user_header(client):
    response = client.patch("/api/time-entries/1/stop")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing X-User-ID header"


# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY UPDATE TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_update_time_entry_success(client):
    payload = {
        "project_id": 1,
        "description": "Initial session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    # Stop the entry first (updates only allowed on finished entries)
    client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    update_payload = {
        "description": "Updated session description",
    }

    response = client.patch(f"/api/time-entries/{entry_id}", json=update_payload, headers=USER_HEADERS)

    assert response.status_code == 200

    entry_data = get_first_result(response)

    assert entry_data["id"] == entry_id
    assert entry_data["description"] == update_payload["description"]
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]


def test_update_time_entry_running_entry_returns_409(client):
    payload = {
        "project_id": 1,
        "description": "Running session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)
    entry_id = get_first_result(response)["id"]

    update_payload = {"description": "Should not update"}

    response = client.patch(f"/api/time-entries/{entry_id}", json=update_payload, headers=USER_HEADERS)

    assert response.status_code == 409
    assert response.get_json()["message"] == "Cannot update a running time entry"


def test_update_time_entry_not_found(client):
    payload = {"description": "Updated"}

    response = client.patch("/api/time-entries/999", json=payload, headers=USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_update_time_entry_other_user_returns_404(client):
    payload = {
        "project_id": 1,
        "description": "User test",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)
    entry_id = get_first_result(response)["id"]

    client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    update_payload = {"description": "Updated"}

    response = client.patch(f"/api/time-entries/{entry_id}", json=update_payload, headers=OTHER_USER_HEADERS)

    assert response.status_code == 404
    assert response.get_json()["message"] == "Time entry not found"


def test_update_time_entry_missing_user_header(client):
    response = client.patch("/api/time-entries/1", json={"description": "Updated"})

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing X-User-ID header"

# ---------------------------------------------------------------------------------------------------------------------
# TIME ENTRY DELETE TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_delete_time_entry_success(client):
    payload = {
        "project_id": 1,
        "description": "Delete test session",
    }

    response = client.post("/api/time-entries", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]

    response = client.delete(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert response.status_code == 204

    response = client.get(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert response.status_code == 404