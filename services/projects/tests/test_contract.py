USER_HEADERS = {"X-User-ID": "123"}


PROJECT_KEYS = {
    "id",
    "owner_user_id",
    "name",
    "description",
}


def assert_results_response(data):
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)


def assert_project_contract(project):
    assert set(project.keys()) == PROJECT_KEYS
    assert isinstance(project["id"], int)
    assert isinstance(project["owner_user_id"], str)
    assert isinstance(project["name"], str)
    assert project["description"] is None or isinstance(project["description"], str)


def test_create_project_response_contract(client):
    response = client.post(
        "/api/projects",
        json={"name": "Contract Project", "description": "Contract test"},
        headers=USER_HEADERS,
    )

    assert response.status_code == 201

    data = response.get_json()
    assert_results_response(data)
    assert len(data["results"]) == 1
    assert_project_contract(data["results"][0])


def test_list_projects_response_contract(client):
    client.post(
        "/api/projects",
        json={"name": "Contract Project"},
        headers=USER_HEADERS,
    )

    response = client.get("/api/projects", headers=USER_HEADERS)

    assert response.status_code == 200

    data = response.get_json()
    assert_results_response(data)

    for project in data["results"]:
        assert_project_contract(project)


def test_missing_user_header_contract(client):
    response = client.get("/api/projects")

    assert response.status_code == 400

    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Missing X-User-ID header"


def test_invalid_create_payload_contract(client):
    response = client.post(
        "/api/projects",
        json={"description": "Missing name"},
        headers=USER_HEADERS,
    )

    assert response.status_code == 422

    data = response.get_json()
    assert "errors" in data
