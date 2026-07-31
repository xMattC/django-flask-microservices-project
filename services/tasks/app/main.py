import os

from flask import Flask
from flask_smorest import Api

from app.extensions import db, migrate
from app.routes import routes


def build_db_uri():
    """Build the SQLAlchemy database URI from environment variables."""
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_port = os.environ.get("DB_PORT", "5432")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def configure_app(app):
    """Configure Flask and database settings."""

    # Configure the database connection used by SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = build_db_uri()

    # Disable SQLAlchemy modification tracking to reduce overhead
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # API metadata used by flask-smorest/OpenAPI documentation
    app.config["API_TITLE"] = "Tasks Service API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


def init_extensions(app):
    """Initialise Flask extensions."""

    # Attach SQLAlchemy to the Flask application
    db.init_app(app)

    # Attach Flask-Migrate for Alembic database migrations
    migrate.init_app(app, db)

    # Ensure SQLAlchemy models are imported so Flask-Migrate
    # can detect database tables and schema changes
    import app.models  # noqa: F401


def register_routes(api):
    """Register the application's API blueprint

    All endpoints defined inside `routes` will be available under the `/api` URL prefix.
    """
    api.register_blueprint(blp=routes, url_prefix="/api")


def create_app():
    """Create and configure the Flask application."""

    # Create the main Flask application instance
    app = Flask(__name__)

    # Apply Flask configuration settings
    configure_app(app)

    # Initialise database and migration extensions
    init_extensions(app)

    # Create the flask-smorest API wrapper
    api = Api(app)

    # Register all API routes/blueprints
    register_routes(api)

    return app
