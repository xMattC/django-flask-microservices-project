from flask import jsonify
from flask_smorest import Blueprint
from werkzeug.exceptions import HTTPException

# from app.extensions import db
# from app.models import Tasks

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
