from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_rule(client: TestClient) -> None:
    response = client.get("/v1/rules/91")
    assert response.status_code == 200
    assert response.json()["number"] == "91"


def test_get_rule_not_found(client: TestClient) -> None:
    response = client.get("/v1/rules/99.3")
    assert response.status_code == 404
    assert response.json() == {"detail": "Rule not found"}
