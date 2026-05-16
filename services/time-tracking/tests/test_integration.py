USER_HEADERS = {"X-User-ID": "123"}
OTHER_USER_HEADERS = {"X-User-ID": "999"}


def first_result(response):
    return response.get_json()["results"][0]


def test_time_entry_crud_integration_flow(client):
    create_response = client.post(
        "/api/time-entries",
        json={"project_id": 1, "description": "Initial session"},
        headers=USER_HEADERS,
    )

    assert create_response.status_code == 201
    entry = first_result(create_response)
    entry_id = entry["id"]

    detail_response = client.get(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert detail_response.status_code == 200
    assert first_result(detail_response)["description"] == "Initial session"

    stop_response = client.patch(f"/api/time-entries/{entry_id}/stop", headers=USER_HEADERS)

    assert stop_response.status_code == 200
    stopped_entry = first_result(stop_response)
    assert stopped_entry["ended_at"] is not None
    assert stopped_entry["duration_seconds"] is not None

    update_response = client.patch(
        f"/api/time-entries/{entry_id}",
        json={"description": "Updated session"},
        headers=USER_HEADERS,
    )

    assert update_response.status_code == 200
    assert first_result(update_response)["description"] == "Updated session"

    list_response = client.get("/api/time-entries", headers=USER_HEADERS)

    assert list_response.status_code == 200
    assert len(list_response.get_json()["results"]) == 1

    delete_response = client.delete(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/time-entries/{entry_id}", headers=USER_HEADERS)

    assert missing_response.status_code == 404


def test_running_time_entry_cannot_be_updated(client):
    create_response = client.post(
        "/api/time-entries",
        json={"project_id": 1, "description": "Running session"},
        headers=USER_HEADERS,
    )

    entry_id = first_result(create_response)["id"]

    update_response = client.patch(
        f"/api/time-entries/{entry_id}",
        json={"description": "Should fail"},
        headers=USER_HEADERS,
    )

    assert update_response.status_code == 409
    assert update_response.get_json()["message"] == "Cannot update a running time entry"


def test_time_entry_user_isolation_integration(client):
    create_response = client.post(
        "/api/time-entries",
        json={"project_id": 1, "description": "Private session"},
        headers=USER_HEADERS,
    )

    entry_id = first_result(create_response)["id"]

    other_user_response = client.get(
        f"/api/time-entries/{entry_id}",
        headers=OTHER_USER_HEADERS,
    )

    assert other_user_response.status_code == 404
