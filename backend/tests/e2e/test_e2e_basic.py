import pytest
from backend.apps.admin_api import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_fluxo_e2e_basico(client):
    # Exemplo: login, operação, logout
    login = client.post("/api/auth/login", json={"username": "teste", "password": "123456"})
    assert login.status_code in (200, 401)  # Ajuste conforme esperado
    if login.status_code == 200:
        token = login.json.get("access_token")
        assert token
        # Exemplo de uso autenticado
        resp = client.get("/api/user/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (200, 403, 404)
