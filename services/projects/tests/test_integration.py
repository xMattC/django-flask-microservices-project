USER_HEADERS = {"X-User-ID": "123"}
OTHER_USER_HEADERS = {"X-User-ID": "999"}


def first_result(response):
    return response.get_json()["results"][0]


def test_project_crud_integration_flow(client):
    create_response = client.post(
        "/api/projects",
        json={"name": "Integration Project", "description": "Initial"},
        headers=USER_HEADERS,
    )

    assert create_response.status_code == 201
    project = first_result(create_response)
    project_id = project["id"]

    detail_response = client.get(f"/api/projects/{project_id}", headers=USER_HEADERS)

    assert detail_response.status_code == 200
    assert first_result(detail_response)["name"] == "Integration Project"

    update_response = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project", "description": "Updated"},
        headers=USER_HEADERS,
    )

    assert update_response.status_code == 200
    updated_project = first_result(update_response)
    assert updated_project["name"] == "Updated Project"
    assert updated_project["description"] == "Updated"

    list_response = client.get("/api/projects", headers=USER_HEADERS)

    assert list_response.status_code == 200
    assert len(list_response.get_json()["results"]) == 1

    delete_response = client.delete(f"/api/projects/{project_id}", headers=USER_HEADERS)

    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/projects/{project_id}", headers=USER_HEADERS)

    assert missing_response.status_code == 404


def test_project_user_isolation_integration(client):
    create_response = client.post(
        "/api/projects",
        json={"name": "Private Project"},
        headers=USER_HEADERS,
    )

    project_id = first_result(create_response)["id"]

    other_user_response = client.get(
        f"/api/projects/{project_id}",
        headers=OTHER_USER_HEADERS,
    )

    assert other_user_response.status_code == 404
