from flask import request
from flask_smorest import Blueprint, abort

from app.open_api_docs import endpoint_docs
from app.extensions import db
from app.models import Project
from app.schemas import (
    ProjectCreateSchema,
    ProjectResultsSchema,
    ProjectUpdateSchema,
)

routes = Blueprint("routes", __name__, description="Projects service endpoints")


# ---------------------------------------------------------------------------------------------------------------------
# Helper functions for route handlers
# ---------------------------------------------------------------------------------------------------------------------
def get_required_user_id():
    """Return the authenticated user ID."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        abort(400, message="Missing X-User-ID header")

    return user_id


def get_owned_project_or_error(project_id, user_id):
    """Return a project owned by the authenticated user."""
    project = Project.query.filter_by(id=project_id, owner_user_id=user_id).first()

    if not project:
        abort(404, message="Project not found")

    return project


# ---------------------------------------------------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------------------------------------------------
@routes.get("/health")
def health():
    """Return a basic service health check."""
    return {"status": "ok"}, 200


@routes.get("/db-health")
def db_health():
    """Return a database connectivity health check."""
    with db.engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return {"database": "ok"}, 200


@routes.post("/projects")
@routes.arguments(ProjectCreateSchema)
@endpoint_docs(routes, success_code=201, response_schema=ProjectResultsSchema)
def create_project(data):
    """Create a new project for the authenticated user."""
    user_id = get_required_user_id()
    project = Project(owner_user_id=user_id, name=data.get("name"), description=data.get("description"))

    db.session.add(project)
    db.session.commit()

    return {"results": [project.to_dict()]}, 201


@routes.get("/projects")
@endpoint_docs(routes, response_schema=ProjectResultsSchema)
def get_all_projects():
    """Return all projects owned by the authenticated user."""
    user_id = get_required_user_id()
    projects = Project.query.filter_by(owner_user_id=user_id).all()

    return {"results": [project.to_dict() for project in projects]}, 200


@routes.get("/projects/<int:project_id>")
@endpoint_docs(routes, response_schema=ProjectResultsSchema, errors=(400, 404))
def get_project_detail(project_id):
    """Return a single project owned by the authenticated user."""
    user_id = get_required_user_id()
    project = get_owned_project_or_error(project_id, user_id)

    return {"results": [project.to_dict()]}, 200


@routes.patch("/projects/<int:project_id>")
@routes.arguments(ProjectUpdateSchema)
@endpoint_docs(routes, response_schema=ProjectResultsSchema, errors=(400, 404))
def update_project(data, project_id):
    """Update a project owned by the authenticated user."""
    user_id = get_required_user_id()
    project = get_owned_project_or_error(project_id, user_id)

    project.name = data.get("name", project.name)
    project.description = data.get("description", project.description)

    db.session.commit()

    return {"results": [project.to_dict()]}, 200


@routes.delete("/projects/<int:project_id>")
@endpoint_docs(routes, success_code=204, response_schema=None, errors=(400, 404))
def delete_project(project_id):
    """Delete a project owned by the authenticated user."""
    user_id = get_required_user_id()
    project = get_owned_project_or_error(project_id, user_id)

    db.session.delete(project)
    db.session.commit()

    return "", 204
