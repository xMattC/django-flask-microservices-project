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

    assert data["id"] is not None
    assert data["name"] == "Test Project"
    assert data["description"] == "My first project"
    assert data["owner_user_id"] == "123"

    with app.app_context():
        project = Project.query.filter_by(owner_user_id="123").first()

    assert project is not None
    assert project.name == "Test Project"
    assert project.description == "My first project"


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
# PROJECT READ TESTS
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

    assert len(data) == 2

    names = [project["name"] for project in data]

    assert "Project 1" in names
    assert "Project 2" in names



# -----------------------------------------------------------------
# PROJECT UPDATE TESTS
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# PROJECT DELETE TESTS
# -----------------------------------------------------------------
