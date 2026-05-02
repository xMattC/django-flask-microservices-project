from app.models import Project

# -----------------------------------------------------------------
# PROJECT CREATE TESTS
# -----------------------------------------------------------------


def test_create_project_success(app, client):
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "My first project",
        },
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 201

    data = response.get_json()
    project_data = data["results"][0]

    assert project_data["id"] is not None
    assert project_data["name"] == "Test Project"
    assert project_data["description"] == "My first project"
    assert project_data["owner_user_id"] == "123"

    with app.app_context():
        project = Project.query.filter_by(owner_user_id="123").first()

    assert project is not None
    assert project.name == "Test Project"
    assert project.description == "My first project"


def test_get_projects_returns_empty_list(client):
    response = client.get(
        "/projects",
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 200

    data = response.get_json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0


def test_create_project_missing_user_header(client):
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "My first project",
        },
    )
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Missing X-User-ID header"


def test_create_project_missing_name(client):
    response = client.post(
        "/projects",
        json={
            "description": "My first project",
        },
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Missing project name"


def test_create_project_empty_name(client):
    response = client.post(
        "/projects",
        json={
            "name": "",
            "description": "My first project",
        },
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Missing project name"


# -----------------------------------------------------------------
# PROJECT READ (LIST) TESTS
# -----------------------------------------------------------------


def test_get_all_projects(client):
    # Create projects for user 123
    client.post(
        "/projects",
        json={"name": "Project 1", "description": "An initial project"},
        headers={"X-User-ID": "123"},
    )
    client.post(
        "/projects",
        json={"name": "Project 2", "description": "A second project"},
        headers={"X-User-ID": "123"},
    )

    response = client.get(
        "/projects",
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 200

    data = response.get_json()
    projects = data["results"]

    names = [project["name"] for project in projects]
    assert len(names) == 2
    assert "Project 1" in names
    assert "Project 2" in names


def test_get_projects_limited_to_user(client):
    # Other user's project
    client.post(
        "/projects",
        json={"name": "Other Project"},
        headers={"X-User-ID": "999"},
    )

    # Current user's project
    client.post(
        "/projects",
        json={"name": "My Project"},
        headers={"X-User-ID": "123"},
    )

    response = client.get(
        "/projects",
        headers={"X-User-ID": "123"},
    )

    data = response.get_json()
    projects = data["results"]

    assert len(projects) == 1
    assert projects[0]["name"] == "My Project"


def test_get_projects_missing_user_header(client):
    response = client.get("/projects")
    assert response.status_code == 400

    data = response.get_json()
    assert data == {"error": "Missing X-User-ID header"}


# -----------------------------------------------------------------
# PROJECT READ (DETAIL) TESTS
# -----------------------------------------------------------------
def test_get_project_detail_success(app, client):
    # Create a project for user 123
    response = client.post(
        "/projects",
        json={"name": "Detail Project", "description": "Project for detail test"},
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 201

    data = response.get_json()
    project_id = data["results"][0]["id"]

    # Get project detail
    response = client.get(
        f"/projects/{project_id}",
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 200

    data = response.get_json()
    project_data = data["results"][0]

    assert project_data["id"] == project_id
    assert project_data["name"] == "Detail Project"
    assert project_data["description"] == "Project for detail test"
    assert project_data["owner_user_id"] == "123"

def test_get_project_detail_not_found(client):
    response = client.get(
        "/projects/999",
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 404

    data = response.get_json()
    assert data == {"error": "Project not found"}


def test_get_project_detail_other_user_returns_404(client):
    # Create a project for user 123
    response = client.post(
        "/projects",
        json={"name": "Detail Project", "description": "Project for detail test"},
        headers={"X-User-ID": "123"},
    )
    assert response.status_code == 201

    data = response.get_json()
    project_id = data["results"][0]["id"]

    # Try to get project detail as a different user
    response = client.get(
        f"/projects/{project_id}",
        headers={"X-User-ID": "456"},
    )
    assert response.status_code == 404

    data = response.get_json()
    assert data == {"error": "Project not found"}


def test_get_project_detail_missing_user_header(client):
    response = client.get("/projects/1")
    assert response.status_code == 400

    data = response.get_json()
    assert data == {"error": "Missing X-User-ID header"}

# -----------------------------------------------------------------
# PROJECT UPDATE TESTS
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# PROJECT DELETE TESTS
# -----------------------------------------------------------------
