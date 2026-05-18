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


def test_create_task_requires_project_id(client):
    payload = {"task_name": "Initial task", "description": "Initial work session"}

    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required field: project_id"


def test_create_task_requires_task_name(client):
    payload = {"project_id": 1, "description": "Initial work session"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required field: task_name"


def test_create_task_requires_user_id_header(client):
    payload = {"project_id": 1, "task_name": "Initial task"}
    response = client.post("/api/tasks", json=payload)

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required header: X-User-ID"


def test_create_task_allows_missing_description(client):
    payload = {"project_id": 1, "task_name": "Initial task"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry = get_first_result(response)

    assert entry["task_name"] == payload["task_name"]
    assert entry["description"] is None


def test_create_task_sets_default_state(client):
    payload = {"project_id": 1, "task_name": "Initial task"}
    response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    entry = get_first_result(response)

    assert entry["state"] == "to-do"


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


def test_get_tasks_returns_empty_list_when_no_tasks_exist(client):
    response = client.get("/api/tasks", headers=USER_HEADERS)

    assert response.status_code == 200

    entries = get_response_data(response)["results"]

    assert entries == []


def test_get_tasks_requires_user_id_header(client):
    response = client.get("/api/tasks")

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required header: X-User-ID"


def test_get_tasks_only_returns_current_user_tasks(client):
    payload = {
        "project_id": 1,
        "task_name": "User task",
    }

    client.post("/api/tasks", json=payload, headers={"X-User-ID": "user-1"})
    client.post("/api/tasks", json=payload, headers={"X-User-ID": "user-2"})

    response = client.get("/api/tasks", headers={"X-User-ID": "user-1"})

    entries = get_response_data(response)["results"]

    assert len(entries) == 1
    assert entries[0]["owner_user_id"] == "user-1"


def test_get_tasks_returns_expected_fields(client):
    payload = {
        "project_id": 1,
        "task_name": "Initial task",
    }

    client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    response = client.get("/api/tasks", headers=USER_HEADERS)

    entry = get_first_result(response)

    expected_fields = {
        "id",
        "owner_user_id",
        "project_id",
        "task_name",
        "description",
        "state",
        "created_at",
        "updated_at",
    }

    assert set(entry.keys()) == expected_fields


def test_get_tasks_returns_default_state(client):
    payload = {
        "project_id": 1,
        "task_name": "Initial task",
    }

    client.post("/api/tasks", json=payload, headers=USER_HEADERS)

    response = client.get("/api/tasks", headers=USER_HEADERS)

    entry = get_first_result(response)

    assert entry["state"] == "to-do"


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


def test_get_task_detail_requires_user_id_header(client):
    response = client.get("/api/tasks/1")

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required header: X-User-ID"


def test_get_task_detail_returns_404_for_missing_task(client):
    response = client.get("/api/tasks/999", headers=USER_HEADERS)

    assert response.status_code == 404
    assert get_response_data(response)["error"] == "Task not found"


def test_get_task_detail_does_not_return_other_users_task(client):
    payload = {"project_id": 1, "task_name": "Private task"}
    create_response = client.post("/api/tasks", json=payload, headers={"X-User-ID": "user-1"})

    task = get_first_result(create_response)

    response = client.get(f"/api/tasks/{task['id']}", headers={"X-User-ID": "user-2"})

    assert response.status_code == 404
    assert get_response_data(response)["error"] == "Task not found"


def test_get_task_detail_returns_expected_fields(client):
    payload = {"project_id": 1, "task_name": "Initial task", "description": "Initial work session"}

    create_response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    created_task = get_first_result(create_response)

    response = client.get(f"/api/tasks/{created_task['id']}", headers=USER_HEADERS)

    task = get_first_result(response)

    expected_fields = {
        "id",
        "owner_user_id",
        "project_id",
        "task_name",
        "description",
        "state",
        "created_at",
        "updated_at",
    }

    assert response.status_code == 200
    assert set(task.keys()) == expected_fields


def test_get_task_detail_returns_correct_task(client):
    payload_1 = {"project_id": 1, "task_name": "First task"}
    payload_2 = {"project_id": 2, "task_name": "Second task"}

    client.post("/api/tasks", json=payload_1, headers=USER_HEADERS)
    create_response = client.post("/api/tasks", json=payload_2, headers=USER_HEADERS)

    created_task = get_first_result(create_response)

    response = client.get(f"/api/tasks/{created_task['id']}", headers=USER_HEADERS)

    task = get_first_result(response)

    assert response.status_code == 200
    assert task["id"] == created_task["id"]
    assert task["task_name"] == payload_2["task_name"]
    assert task["project_id"] == payload_2["project_id"]


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


def test_update_task_requires_user_id_header(client):
    response = client.patch("/api/tasks/1", json={"task_name": "Updated task"})

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required header: X-User-ID"


def test_update_task_returns_404_for_missing_task(client):
    response = client.patch("/api/tasks/999", json={"task_name": "Updated task"}, headers=USER_HEADERS)

    assert response.status_code == 404
    assert get_response_data(response)["error"] == "Task not found"


def test_update_task_cannot_modify_other_users_task(client):
    payload = {"project_id": 1, "task_name": "Private task"}

    create_response = client.post("/api/tasks", json=payload, headers={"X-User-ID": "user-1"})

    task = get_first_result(create_response)

    response = client.patch(f"/api/tasks/{task['id']}", json={"task_name": "Hacked"}, headers={"X-User-ID": "user-2"})

    assert response.status_code == 404


def test_update_task_updates_only_provided_fields(client):
    payload = {"project_id": 1, "task_name": "Original", "description": "Original description"}

    create_response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    task = get_first_result(create_response)

    response = client.patch(f"/api/tasks/{task['id']}", json={"task_name": "Updated"}, headers=USER_HEADERS)

    updated = get_first_result(response)

    assert updated["task_name"] == "Updated"
    assert updated["description"] == "Original description"


def test_update_task_updates_state(client):
    payload = {"project_id": 1, "task_name": "Initial task"}

    create_response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    task = get_first_result(create_response)

    response = client.patch(f"/api/tasks/{task['id']}", json={"state": "done"}, headers=USER_HEADERS)

    updated = get_first_result(response)

    assert updated["state"] == "done"


# ---------------------------------------------------------------------------------------------------------------------
# TASK DELETE TESTS
# ---------------------------------------------------------------------------------------------------------------------
def test_delete_task_success(client, app):
    payload = {"project_id": 1, "task_name": "Task to delete"}
    create_response = client.post("/api/tasks", json=payload, headers=USER_HEADERS)
    task = get_first_result(create_response)

    response = client.delete(f"/api/tasks/{task['id']}", headers=USER_HEADERS)

    assert response.status_code == 204

    with app.app_context():
        deleted_task = Tasks.query.filter_by(id=task["id"]).first()

    assert deleted_task is None


def test_delete_task_requires_user_id_header(client):
    response = client.delete("/api/tasks/1")

    assert response.status_code == 400
    assert get_response_data(response)["error"] == "Missing required header: X-User-ID"


def test_delete_task_cannot_delete_other_users_task(client, app):
    payload = {"project_id": 1, "task_name": "Private task"}

    create_response = client.post("/api/tasks", json=payload, headers={"X-User-ID": "user-1"})

    task = get_first_result(create_response)

    response = client.delete(f"/api/tasks/{task['id']}", headers={"X-User-ID": "user-2"})

    assert response.status_code == 404

    with app.app_context():
        existing_task = Tasks.query.filter_by(id=task["id"]).first()

    assert existing_task is not None


def test_delete_task_removes_only_target_task(client, app):
    payload_1 = {"project_id": 1, "task_name": "First task"}
    payload_2 = {"project_id": 2, "task_name": "Second task"}

    first_response = client.post("/api/tasks", json=payload_1, headers=USER_HEADERS)
    second_response = client.post("/api/tasks", json=payload_2, headers=USER_HEADERS)

    first_task = get_first_result(first_response)
    second_task = get_first_result(second_response)

    response = client.delete(f"/api/tasks/{first_task['id']}", headers=USER_HEADERS)

    assert response.status_code == 204

    with app.app_context():
        deleted_task = Tasks.query.filter_by(id=first_task["id"]).first()
        remaining_task = Tasks.query.filter_by(id=second_task["id"]).first()

    assert deleted_task is None
    assert remaining_task is not None
