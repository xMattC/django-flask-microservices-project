from flask import Blueprint, request

from app.extensions import db
from app.models import Project

routes = Blueprint("routes", __name__)


@routes.get("/health")
def health():
    """Return basic service health status.

    return: JSON health response and HTTP status code.
    """
    return {"status": "ok"}, 200


@routes.get("/db-health")
def db_health():
    """Check the database connection.

    return: JSON database health response and HTTP status code.
    """
    with db.engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return {"database": "ok"}, 200


@routes.post("/projects")
def create_project():
    """Create a new project.

    return: Created project response and HTTP status code.
    """
    data = request.get_json() or {}

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return {"error": "Missing X-User-ID header"}, 400

    project = Project(owner_user_id=user_id, name=data.get("name"), description=data.get("description"))
    if not project.name:
        return {"error": "Missing project name"}, 400

    db.session.add(project)
    db.session.commit()

    return {"results": [project.to_dict()]}, 201


@routes.get("/projects")
def get_all_projects():
    """Get all projects for the authenticated user.

    return: List of projects and HTTP status code.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return {"error": "Missing X-User-ID header"}, 400

    projects = Project.query.filter_by(owner_user_id=user_id).all()

    return {"results": [project.to_dict() for project in projects]}, 200


@routes.get("/projects/<int:project_id>")
def get_project_detail(project_id):
    """Get a single project for the authenticated user.

    param project_id: ID of the project.
    return: Project detail and HTTP status code.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return {"error": "Missing X-User-ID header"}, 400

    project = Project.query.filter_by(id=project_id, owner_user_id=user_id).first()
    if not project:
        return {"error": "Project not found"}, 404

    return {"results": [project.to_dict()]}, 200
