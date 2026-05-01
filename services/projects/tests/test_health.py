import pytest
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.test_client() as client:
        yield client


def test_health_endpoint_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_returns_expected_body(client):
    response = client.get("/health")

    assert response.get_json() == {"status": "ok"}
