import os

from flask import Flask

from app.extensions import db, migrate
from app.routes import routes


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


def _init_extensions(app):
    """Initialise Flask extensions.

    param app: Flask application instance.
    return: None.
    """
    db.init_app(app)
    migrate.init_app(app, db)


def create_app():
    """Create and configure the Flask application.

    return: Configured Flask application instance.
    """
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = _build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    _init_extensions(app)

    app.register_blueprint(routes)

    return app