from datetime import datetime, timezone

from flask import jsonify, request
from flask_smorest import Blueprint
from werkzeug.exceptions import HTTPException

from app.extensions import db
from app.models import TimeEntry
from app.open_api_docs import endpoint_docs
from app.schemas import (
    TimeEntryCreateSchema,
    TimeEntryResultsSchema,
    TimeEntryUpdateSchema,
)

routes = Blueprint("routes", __name__, description="Time tracking service endpoints")

# ---------------------------------------------------------------------------------------------------------------------
# Helper functions for route handlers
# ---------------------------------------------------------------------------------------------------------------------


@routes.get("/health")
@endpoint_docs(routes)
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


@routes.post("/time-entries")
@routes.arguments(TimeEntryCreateSchema)
@endpoint_docs(routes, success_code=201, response_schema=TimeEntryResultsSchema, errors=(400,))
def create_time_entry(data):
    """Create a new time entry."""

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry(
        owner_user_id=user_id,
        project_id=data["project_id"],
        description=data.get("description"),
        started_at=datetime.now(timezone.utc),
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 201


@routes.get("/time-entries")
@endpoint_docs(routes, response_schema=TimeEntryResultsSchema, errors=(400,))
def list_time_entries():
    """List all time entries. Can be filtered by project_id and running_only if provided."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    query = TimeEntry.query.filter_by(owner_user_id=user_id)

    project_id = request.args.get("project_id")
    if project_id is not None:
        query = query.filter_by(project_id=project_id)

    running_only = request.args.get("running_only")
    if running_only == "true":
        query = query.filter(TimeEntry.ended_at.is_(None))

    entries = query.all()

    return jsonify({"results": [entry.to_dict() for entry in entries]}), 200


@routes.get("/time-entries/<int:entry_id>")
@endpoint_docs(routes, response_schema=TimeEntryResultsSchema, errors=(400, 404))
def get_time_entry_detail(entry_id):
    """Get a single time entry."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry.query.filter_by(id=entry_id, owner_user_id=user_id).first()

    if not entry:
        return jsonify({"message": "Time entry not found"}), 404

    return jsonify({"results": [entry.to_dict()]}), 200


@routes.patch("/time-entries/<int:entry_id>/stop")
@endpoint_docs(routes, response_schema=TimeEntryResultsSchema, errors=(400, 404))
def stop_time_entry(entry_id):
    """Stop a running time entry."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry.query.filter_by(id=entry_id, owner_user_id=user_id).first()

    if not entry:
        return jsonify({"message": "Time entry not found"}), 404

    if entry.ended_at is None:
        entry.ended_at = datetime.now(timezone.utc)
        db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 200


@routes.patch("/time-entries/<int:entry_id>")
@routes.arguments(TimeEntryUpdateSchema)
@endpoint_docs(routes, response_schema=TimeEntryResultsSchema, errors=(400, 404, 409))
def update_time_entry(data, entry_id):
    """Update a finished time entry."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry.query.filter_by(id=entry_id, owner_user_id=user_id).first()

    if not entry:
        return jsonify({"message": "Time entry not found"}), 404

    if entry.ended_at is None:
        return jsonify({"message": "Cannot update a running time entry"}), 409

    if "description" in data:
        entry.description = data["description"]

    if "project_id" in data:
        entry.project_id = data["project_id"]

    db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 200


@routes.delete("/time-entries/<int:entry_id>")
@endpoint_docs(routes, success_code=204, errors=(400, 404))
def delete_time_entry(entry_id):
    """Delete a time entry."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry.query.filter_by(id=entry_id, owner_user_id=user_id).first()

    if not entry:
        return jsonify({"message": "Time entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()

    return "", 204
