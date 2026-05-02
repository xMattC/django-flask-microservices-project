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

    project = Project(
        owner_user_id=user_id,
        name=data.get("name"),
        description=data.get("description"),
    )

    db.session.add(project)
    db.session.commit()

    return {
        "id": project.id,
        "owner_user_id": project.owner_user_id,
        "name": project.name,
        "description": project.description,
    }, 201