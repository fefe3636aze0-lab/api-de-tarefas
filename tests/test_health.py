from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "database": "ok",
    }

def test_lista_tarefas_exige_api_key():
    resposta = client.get("/tarefas")

    assert resposta.status_code == 401

def test_limite_zero_e_rejeitado(monkeypatch):
    monkeypatch.setenv("API_KEY", "chave-de-teste")

    resposta = client.get(
        "/tarefas",
        headers={"X-API-Key": "chave-de-teste"},
        params={"limite": 0},
    )

    assert resposta.status_code == 422