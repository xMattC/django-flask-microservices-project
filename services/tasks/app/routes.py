from asyncio import tasks
from datetime import datetime, timezone
from flask import jsonify, request
from flask_smorest import Blueprint
from werkzeug.exceptions import HTTPException

from app.extensions import db
from app.models import Tasks

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


# ---------------------------------------------------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------------------------------------------------
@routes.post("/tasks")
def create_task():
    """Create a new task."""

    data = request.get_json(silent=True) or {}
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"error": "Missing required header: X-User-ID"}), 400

    for field in ["project_id", "task_name"]:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    entry = Tasks(
        owner_user_id=user_id,
        project_id=data["project_id"],
        task_name=data["task_name"],
        description=data.get("description"),
        state="to-do",
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 201


@routes.get("/tasks")
def get_tasks():
    """Get all tasks for the current user."""

    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"error": "Missing required header: X-User-ID"}), 400

    tasks = Tasks.query.filter_by(owner_user_id=user_id).all()

    return jsonify({"results": [task.to_dict() for task in tasks]}), 200


@routes.get("/tasks/<int:task_id>")
def get_task_detail(task_id):
    """Get a specific task."""

    user_id = request.headers.get("X-User-ID")
    task = Tasks.query.filter_by(id=task_id, owner_user_id=user_id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"results": [task.to_dict()]}), 200


@routes.patch("/tasks/<int:task_id>")
def update_task(task_id):
    """Update a task owned by the authenticated user."""
    user_id = request.headers.get("X-User-ID")
    task = Tasks.query.filter_by(id=task_id, owner_user_id=user_id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.task_name = data.get("task_name", task.task_name)
    task.description = data.get("description", task.description)
    task.state = data.get("state", task.state)

    db.session.commit()

    return jsonify({"results": [task.to_dict()]}), 200


@routes.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    user_id = request.headers.get("X-User-ID")
    task = Tasks.query.filter_by(id=task_id, owner_user_id=user_id).first()

    db.session.delete(task)
    db.session.commit()

    return "", 204
