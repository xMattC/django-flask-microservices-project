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
    payload = {"project_id": 1, "task_name": "Initial task", "description": "Initial work session"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    assert response.status_code == 201

    entry_data = get_first_result(response)
    assert entry_data["id"] is not None
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["description"] == payload["description"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]
    assert entry_data["created_at"] is not None
    assert entry_data["updated_at"] is not None

    with app.app_context():
        entry = Tasks.query.filter_by(owner_user_id=USER_HEADERS["X-User-ID"]).first()

    assert entry is not None
    assert entry.project_id == payload["project_id"]
    assert entry.description == payload["description"]


# ---------------------------------------------------------------------------------------------------------------------
# TASK READ (LIST) TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_get_all_tasks(client):
    payload_1 = {"project_id": 1, "task_name": "Initial task", "description": "Initial work session"}
    payload_2 = {"project_id": 2, "task_name": "Second task", "description": "Second work session"}

    client.post("/api/tasks", json=payload_1, headers=USER_HEADERS)
    client.post("/api/tasks", json=payload_2, headers=USER_HEADERS)

    response = client.get("/api/tasks", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]
    descriptions = [entry["description"] for entry in entries]

    assert len(entries) == 2
    assert payload_1["description"] in descriptions
    assert payload_2["description"] in descriptions


# ---------------------------------------------------------------------------------------------------------------------
# TASK READ (DETAIL) TESTS
# ---------------------------------------------------------------------------------------------------------------------


def test_get_task_detail_success(client):
    payload = {"project_id": 1, "task_name": "Initial task", "description": "Initial work session"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]
    response = client.get(f"/api/tasks/{entry_id}", headers=USER_HEADERS)
    assert response.status_code == 200

    entry_data = get_first_result(response)
    assert entry_data["id"] == entry_id
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["task_name"] == payload["task_name"]
    assert entry_data["description"] == payload["description"]
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]


# ---------------------------------------------------------------------------------------------------------------------
# TASK UPDATE TESTS
# ---------------------------------------------------------------------------------------------------------------------

def test_update_task_success(client):

    payload = {"project_id": 1, "task_name": "Initial task", "description": "Initial work session"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    assert response.status_code == 201

    entry_id = get_first_result(response)["id"]
    update_payload = {"description": "Updated session description", "state": "in-progress"}

    response = client.patch(f"/api/tasks/{entry_id}", json=update_payload, headers=USER_HEADERS)
    assert response.status_code == 200

    entry_data = get_first_result(response)
    assert entry_data["id"] == entry_id
    assert entry_data["owner_user_id"] == USER_HEADERS["X-User-ID"]
    assert entry_data["project_id"] == payload["project_id"]
    assert entry_data["task_name"] == payload["task_name"]
    assert entry_data["description"] == update_payload["description"]
    assert entry_data["state"] == update_payload["state"]



# ---------------------------------------------------------------------------------------------------------------------
# TASK DELETE TESTS
# ---------------------------------------------------------------------------------------------------------------------
def test_delete_task_success(client):
    pass
