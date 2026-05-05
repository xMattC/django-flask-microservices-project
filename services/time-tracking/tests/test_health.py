def test_health_endpoint_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_returns_expected_body(client):
    response = client.get("/health")

    assert response.get_json() == {"status": "ok"}

