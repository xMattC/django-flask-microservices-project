import pytest

from app.extensions import db
from app.main import create_app


@pytest.fixture
def app():
    """Create a Flask test app with a clean database.

    return: Configured Flask application instance.
    """
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a Flask test client.

    param app: Flask application instance.
    return: Flask test client.
    """
    return app.test_client()