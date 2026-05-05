from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import TimeEntry

routes = Blueprint("routes", __name__)

# ---------------------------------------------------------------------------------------------------------------------
# Helper functions for route handlers
# ---------------------------------------------------------------------------------------------------------------------


@routes.get("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@routes.errorhandler(Exception)
def handle_exception(error):
    """Handle unexpected exceptions."""
    return jsonify({"message": "Internal server error"}), 500


@routes.get("/db-health")
def db_health():
    """Check the database connection."""
    with db.engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return jsonify({"database": "ok"}), 200


# ---------------------------------------------------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------------------------------------------------


@routes.post("/time-entries")
def create_time_entry():
    """Create a new time entry."""

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    data = request.get_json() or {}
    project_id = data.get("project_id")
    description = data.get("description")

    if project_id is None:
        return jsonify({"errors": {"project_id": "This field is required"}}), 422

    entry = TimeEntry(
        owner_user_id=user_id,
        project_id=project_id,
        description=description,
        started_at=datetime.now(timezone.utc),
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 201


@routes.get("/time-entries")
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
def update_time_entry(entry_id):
    """Update a finished time entry."""
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        return jsonify({"message": "Missing X-User-ID header"}), 400

    entry = TimeEntry.query.filter_by(id=entry_id, owner_user_id=user_id).first()

    if not entry:
        return jsonify({"message": "Time entry not found"}), 404

    if entry.ended_at is None:
        return jsonify({"message": "Cannot update a running time entry"}), 409

    data = request.get_json() or {}

    description = data.get("description")
    project_id = data.get("project_id")

    if description is not None:
        entry.description = description

    if project_id is not None:
        entry.project_id = project_id

    db.session.commit()

    return jsonify({"results": [entry.to_dict()]}), 200


@routes.delete("/time-entries/<int:entry_id>")
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
