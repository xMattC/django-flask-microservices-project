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
