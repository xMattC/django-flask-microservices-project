from flask import Blueprint, jsonify
from app.extensions import db

routes = Blueprint("routes", __name__)


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
