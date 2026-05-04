import os

from flask import Flask

from app.extensions import api, db, migrate
from app.routes import routes


# -------------------------------------------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------------------------------------------
def _build_db_uri():
    """Build the SQLAlchemy database URI from environment variables.

    return: PostgreSQL database connection URI.
    """
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_port = os.environ.get("DB_PORT", "5432")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# -------------------------------------------------------------------------------------------------
# Application configuration
# -------------------------------------------------------------------------------------------------
def _configure_app(app):
    """Configure Flask, database, and OpenAPI settings.

    param app: Flask application instance.
    return: None.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = _build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["API_TITLE"] = "Projects Service API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


# -------------------------------------------------------------------------------------------------
# Extension initialisation
# -------------------------------------------------------------------------------------------------
def _init_extensions(app):
    """Initialise Flask extensions.

    param app: Flask application instance.
    return: None.
    """
    db.init_app(app)
    migrate.init_app(app, db)


# -------------------------------------------------------------------------------------------------
# Blueprint registration
# -------------------------------------------------------------------------------------------------
def _register_blueprints():
    """Register Flask-Smorest blueprints.

    return: None.
    """
    api.register_blueprint(routes, url_prefix="/api")


# -------------------------------------------------------------------------------------------------
# Application factory
# -------------------------------------------------------------------------------------------------
def create_app():
    """Create and configure the Flask application.

    return: Configured Flask application instance.
    """
    app = Flask(__name__)

    _configure_app(app)
    _init_extensions(app)

    api.init_app(app)
    _register_blueprints()

    return app
