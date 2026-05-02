from app.models import Project

USER_HEADERS = {"X-User-ID": "123"}
OTHER_USER_HEADERS = {"X-User-ID": "999"}


def get_response_data(response):
    """Return JSON response data.

    param response: Flask test response.
    return: Parsed JSON response data.
    """
    return response.get_json()


def get_first_result(response):
    """Return the first item from a results response.

    param response: Flask test response.
    return: First result item from the JSON response.
    """
    return get_response_data(response)["results"][0]


# -----------------------------------------------------------------
# PROJECT CREATE TESTS
# -----------------------------------------------------------------


def test_create_project_success(app, client):
    payload = {
        "name": "Test Project",
        "description": "My first project",
    }

    response = client.post("/projects", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    project_data = get_first_result(response)

    assert project_data["id"] is not None
    assert project_data["name"] == payload["name"]
    assert project_data["description"] == payload["description"]
    assert project_data["owner_user_id"] == USER_HEADERS["X-User-ID"]

    with app.app_context():
        project = Project.query.filter_by(owner_user_id=USER_HEADERS["X-User-ID"]).first()

    assert project is not None
    assert project.name == payload["name"]
    assert project.description == payload["description"]


def test_create_project_missing_user_header(client):
    payload = {
        "name": "Test Project",
        "description": "My first project",
    }

    response = client.post("/projects", json=payload)

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing X-User-ID header"}


def test_create_project_missing_name(client):
    payload = {
        "description": "My first project",
    }

    response = client.post("/projects", json=payload, headers=USER_HEADERS)

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing project name"}


def test_create_project_empty_name(client):
    payload = {
        "name": "",
        "description": "My first project",
    }

    response = client.post("/projects", json=payload, headers=USER_HEADERS)

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing project name"}


# -----------------------------------------------------------------
# PROJECT READ (LIST) TESTS
# -----------------------------------------------------------------


def test_get_projects_returns_empty_list(client):
    response = client.get("/projects", headers=USER_HEADERS)

    assert response.status_code == 200

    data = get_response_data(response)

    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0


def test_get_all_projects(client):
    payload_1 = {"name": "Project 1", "description": "An initial project"}
    payload_2 = {"name": "Project 2", "description": "A second project"}

    client.post("/projects", json=payload_1, headers=USER_HEADERS)
    client.post("/projects", json=payload_2, headers=USER_HEADERS)

    response = client.get("/projects", headers=USER_HEADERS)

    assert response.status_code == 200

    projects = get_response_data(response)["results"]
    names = [project["name"] for project in projects]

    assert len(names) == 2
    assert payload_1["name"] in names
    assert payload_2["name"] in names


def test_get_projects_limited_to_user(client):
    other_user_payload = {"name": "Other Project"}
    current_user_payload = {"name": "My Project"}

    client.post("/projects", json=other_user_payload, headers=OTHER_USER_HEADERS)
    client.post("/projects", json=current_user_payload, headers=USER_HEADERS)

    response = client.get("/projects", headers=USER_HEADERS)

    assert response.status_code == 200

    projects = get_response_data(response)["results"]

    assert len(projects) == 1
    assert projects[0]["name"] == current_user_payload["name"]


def test_get_projects_missing_user_header(client):
    response = client.get("/projects")

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing X-User-ID header"}


# -----------------------------------------------------------------
# PROJECT READ (DETAIL) TESTS
# -----------------------------------------------------------------


def test_get_project_detail_success(client):
    payload = {
        "name": "Detail Project",
        "description": "Project for detail test",
    }

    response = client.post("/projects", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    project_id = get_first_result(response)["id"]

    response = client.get(f"/projects/{project_id}", headers=USER_HEADERS)

    assert response.status_code == 200

    project_data = get_first_result(response)

    assert project_data["id"] == project_id
    assert project_data["name"] == payload["name"]
    assert project_data["description"] == payload["description"]
    assert project_data["owner_user_id"] == USER_HEADERS["X-User-ID"]


def test_get_project_detail_not_found(client):
    response = client.get("/projects/999", headers=USER_HEADERS)

    assert response.status_code == 404
    assert get_response_data(response) == {"error": "Project not found"}


def test_get_project_detail_other_user_returns_404(client):
    payload = {
        "name": "Detail Project",
        "description": "Project for detail test",
    }

    response = client.post("/projects", json=payload, headers=USER_HEADERS)

    assert response.status_code == 201

    project_id = get_first_result(response)["id"]

    response = client.get(f"/projects/{project_id}", headers={"X-User-ID": "456"})

    assert response.status_code == 404
    assert get_response_data(response) == {"error": "Project not found"}


def test_get_project_detail_missing_user_header(client):
    response = client.get("/projects/1")

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing X-User-ID header"}


# -----------------------------------------------------------------
# PROJECT UPDATE TESTS
# -----------------------------------------------------------------


def test_update_project_success(client):
    create_payload = {
        "name": "Old Project",
        "description": "Old description",
    }
    response = client.post("/projects", json=create_payload, headers=USER_HEADERS)

    assert response.status_code == 201

    project_id = get_first_result(response)["id"]

    update_payload = {"name": "Updated Project", "description": "Updated description"}
    response = client.patch(f"/projects/{project_id}", json=update_payload, headers=USER_HEADERS)

    assert response.status_code == 200

    project_data = get_first_result(response)

    assert project_data["id"] == project_id
    assert project_data["name"] == update_payload["name"]
    assert project_data["description"] == update_payload["description"]
    assert project_data["owner_user_id"] == USER_HEADERS["X-User-ID"]


def test_update_project_partial_name_only(client):
    create_payload = {
        "name": "Old Project",
        "description": "Old description",
    }
    response = client.post("/projects", json=create_payload, headers=USER_HEADERS)
    project_id = get_first_result(response)["id"]

    update_payload = {"name": "Updated Project"}
    response = client.patch(f"/projects/{project_id}", json=update_payload, headers=USER_HEADERS)

    assert response.status_code == 200

    project_data = get_first_result(response)

    assert project_data["name"] == "Updated Project"
    assert project_data["description"] == "Old description"


def test_update_project_missing_user_header(client):
    response = client.patch("/projects/1", json={"name": "Updated Project"})

    assert response.status_code == 400
    assert get_response_data(response) == {"error": "Missing X-User-ID header"}


def test_update_project_not_found(client):
    payload = {"name": "Updated Project"}
    response = client.patch("/projects/999", json=payload, headers=USER_HEADERS)

    assert response.status_code == 404
    assert get_response_data(response) == {"error": "Project not found"}


def test_update_project_other_user_returns_404(client):
    post_payload = {"name": "My Project"}
    response = client.post("/projects", json=post_payload, headers=USER_HEADERS)

    project_id = get_first_result(response)["id"]

    update_payload = {"name": "Updated Project"}
    response = client.patch(f"/projects/{project_id}", json=update_payload, headers={"X-User-ID": "999"})

    assert response.status_code == 404
    assert get_response_data(response) == {"error": "Project not found"}


# -----------------------------------------------------------------
# PROJECT DELETE TESTS
# -----------------------------------------------------------------
def test_delete_project_success(client):
    payload = {"name": "Project to delete"}
    response = client.post("/projects", json=payload, headers=USER_HEADERS)
    assert response.status_code == 201

    project_id = get_first_result(response)["id"]
    response = client.delete(f"/projects/{project_id}", headers=USER_HEADERS)
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}", headers=USER_HEADERS)

    assert response.status_code == 404
