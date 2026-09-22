from fastapi.testclient import TestClient

from pdd_ai_coach.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_rule() -> None:
    response = client.get("/v1/rules/10.2")
    assert response.status_code == 200
    assert response.json()["number"] == "10.2"


def test_get_rule_not_found() -> None:
    response = client.get("/v1/rules/99.3")
    assert response.status_code == 404
    assert response.json() == {"detail": "Rule not found"}
