from flask import jsonify, request
from flask_smorest import Blueprint
from werkzeug.exceptions import HTTPException

from app.extensions import db
from app.models import Tasks
from app.open_api_docs import endpoint_docs
from app.schemas import (
    TaskCreateSchema,
    TaskResultsSchema,
    TaskUpdateSchema,
)

routes = Blueprint("routes", __name__, description="Tasks service endpoints")


# ---------------------------------------------------------------------------------------------------------------------
# Health check and error handlers
# ---------------------------------------------------------------------------------------------------------------------


@routes.get("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@routes.errorhandler(Exception)
def handle_exception(error):
    """Handle unexpected exceptions."""
    if isinstance(error, HTTPException):
        return error

    return jsonify({"message": "Internal server error"}), 500


@routes.get("/db-health")
@endpoint_docs(routes)
def db_health():
    """Check the database connection."""
    with db.engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return jsonify({"database": "ok"}), 200


# ---------------------------------------------------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------------------------------------------------


@routes.post("/tasks")
@routes.arguments(TaskCreateSchema)
@endpoint_docs(routes, success_code=201, response_schema=TaskResultsSchema, errors=(400, 422))
def create_task(data):
    """Create a new task."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing required header: X-User-ID"}), 400

    task = Tasks(
        owner_user_id=user_id,
        project_id=data["project_id"],
        task_name=data["task_name"],
        description=data.get("description"),
        state=data.get("state", "to-do"),
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"results": [task.to_dict()]}), 201


@routes.get("/tasks")
@endpoint_docs(routes, response_schema=TaskResultsSchema)
def get_tasks():
    """Get all tasks for the current user."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing required header: X-User-ID"}), 400

    tasks = Tasks.query.filter_by(owner_user_id=user_id).all()

    return jsonify({"results": [task.to_dict() for task in tasks]}), 200


@routes.get("/tasks/<int:task_id>")
@endpoint_docs(routes, response_schema=TaskResultsSchema, errors=(400, 404))
def get_task_detail(task_id):
    """Get a specific task."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing required header: X-User-ID"}), 400

    task = Tasks.query.filter_by(
        id=task_id,
        owner_user_id=user_id,
    ).first()

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    return jsonify({"results": [task.to_dict()]}), 200


@routes.patch("/tasks/<int:task_id>")
@routes.arguments(TaskUpdateSchema)
@endpoint_docs(routes, response_schema=TaskResultsSchema, errors=(400, 404, 422))
def update_task(data, task_id):
    """Update a task owned by the authenticated user."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing required header: X-User-ID"}), 400

    task = Tasks.query.filter_by(
        id=task_id,
        owner_user_id=user_id,
    ).first()

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    task.task_name = data.get("task_name", task.task_name)
    task.description = data.get("description", task.description)
    task.project_id = data.get("project_id", task.project_id)
    task.state = data.get("state", task.state)

    db.session.commit()

    return jsonify({"results": [task.to_dict()]}), 200


@routes.delete("/tasks/<int:task_id>")
@endpoint_docs(routes, success_code=204, errors=(400, 404))
def delete_task(task_id):
    """Delete a task owned by the authenticated user."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing required header: X-User-ID"}), 400

    task = Tasks.query.filter_by(id=task_id, owner_user_id=user_id).first()

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return "", 204
