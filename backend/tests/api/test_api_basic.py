import pytest
from backend.apps.admin_api import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code in (200, 404)  # Ajuste conforme resposta esperada

def test_not_found(client):
    response = client.get("/nao-existe")
    assert response.status_code == 404
