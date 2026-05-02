from app.extensions import db
from app.main import create_app
from app.models import Project


def test_create_project_success():
    app = create_app()
    app.config.update({"TESTING": True})

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
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

def test_create_project_missing_user_header():
    app = create_app()
    app.config.update({"TESTING": True})

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
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

def test_create_project_missing_name():
    app = create_app()
    app.config.update({"TESTING": True})

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        response = client.post(
            "/projects",
            json={
                "description": "My first project",
            },
            headers={"X-User-ID": "123"},
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing Project Name"


def test_create_project_empty_name():
    app = create_app()
    app.config.update({"TESTING": True})

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
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

    assert data["error"] == "Missing Project Name"

