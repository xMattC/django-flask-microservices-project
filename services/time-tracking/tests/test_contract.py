USER_HEADERS = {"X-User-ID": "123"}


TIME_ENTRY_KEYS = {
    "id",
    "owner_user_id",
    "project_id",
    "description",
    "started_at",
    "ended_at",
    "duration_seconds",
    "created_at",
    "updated_at",
}


def assert_results_response(data):
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)


def assert_time_entry_contract(entry):
    assert set(entry.keys()) == TIME_ENTRY_KEYS
    assert isinstance(entry["id"], int)
    assert isinstance(entry["owner_user_id"], str)
    assert isinstance(entry["project_id"], int)
    assert entry["description"] is None or isinstance(entry["description"], str)
    assert isinstance(entry["started_at"], str)
    assert entry["ended_at"] is None or isinstance(entry["ended_at"], str)
    assert entry["duration_seconds"] is None or isinstance(entry["duration_seconds"], int)
    assert isinstance(entry["created_at"], str)
    assert isinstance(entry["updated_at"], str)


def test_create_time_entry_response_contract(client):
    response = client.post(
        "/api/time-entries",
        json={"project_id": 1, "description": "Contract session"},
        headers=USER_HEADERS,
    )

    assert response.status_code == 201

    data = response.get_json()
    assert_results_response(data)
    assert len(data["results"]) == 1
    assert_time_entry_contract(data["results"][0])


def test_list_time_entries_response_contract(client):
    client.post(
        "/api/time-entries",
        json={"project_id": 1, "description": "Contract session"},
        headers=USER_HEADERS,
    )

    response = client.get("/api/time-entries", headers=USER_HEADERS)

    assert response.status_code == 200

    data = response.get_json()
    assert_results_response(data)

    for entry in data["results"]:
        assert_time_entry_contract(entry)


def test_missing_user_header_contract(client):
    response = client.get("/api/time-entries")

    assert response.status_code == 400

    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Missing X-User-ID header"


def test_invalid_create_payload_contract(client):
    response = client.post(
        "/api/time-entries",
        json={"description": "Missing project ID"},
        headers=USER_HEADERS,
    )

    assert response.status_code == 422
