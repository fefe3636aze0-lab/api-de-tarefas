import banco
import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_criar_tarefa_e_encontrar_na_lista(tmp_path, monkeypatch):
    banco_teste = tmp_path / "teste.db"

    monkeypatch.setattr(main, "DB_PATH", banco_teste)
    monkeypatch.setattr(banco, "DB_PATH", banco_teste)
    monkeypatch.setenv("API_KEY", "chave-de-teste")

    banco.iniciar_banco()

    cabecalhos = {"X-API-Key": "chave-de-teste"}

    resposta = client.post(
        "/tarefas",
        headers=cabecalhos,
        json={
            "titulo": "Estudar testes",
            "concluida": False,
            "prioridade": "alta",
        },
    )

    assert resposta.status_code == 201

    tarefa_criada = resposta.json()
    assert tarefa_criada["titulo"] == "Estudar testes"
    assert tarefa_criada["prioridade"] == "alta"

    lista = client.get("/tarefas", headers=cabecalhos)

    assert lista.status_code == 200
    assert lista.json()["itens"] == [tarefa_criada]

def test_lista_ordena_prioridade_alta_primeiro(tmp_path, monkeypatch):
    banco_teste = tmp_path / "prioridades.db"

    monkeypatch.setattr(main, "DB_PATH", banco_teste)
    monkeypatch.setattr(banco, "DB_PATH", banco_teste)
    monkeypatch.setenv("API_KEY", "chave-de-teste")

    banco.iniciar_banco()

    cabecalhos = {"X-API-Key": "chave-de-teste"}

    # Criamos em ordem baixa, alta, média para conferir a ordenação.
    for titulo, prioridade in [
        ("Pouco urgente", "Low"),
        ("Urgente", "High"),
        ("Normal", "Medium"),
    ]:
        resposta = client.post(
            "/tarefas",
            headers=cabecalhos,
            json={
                "titulo": titulo,
                "concluida": False,
                "prioridade": prioridade,
            },
        )
        assert resposta.status_code == 201

    resposta = client.get("/tarefas", headers=cabecalhos)

    assert resposta.status_code == 200
    prioridades = [
        tarefa["prioridade"]
        for tarefa in resposta.json()["itens"]
    ]
    assert prioridades == ["High", "Medium", "Low"]
def test_atualizar_e_apagar_tarefa(tmp_path, monkeypatch):
    banco_teste = tmp_path / "atualizar-apagar.db"

    monkeypatch.setattr(main, "DB_PATH", banco_teste)
    monkeypatch.setattr(banco, "DB_PATH", banco_teste)
    monkeypatch.setenv("API_KEY", "chave-de-teste")

    banco.iniciar_banco()

    cabecalhos = {"X-API-Key": "chave-de-teste"}

    criada = client.post(
        "/tarefas",
        headers=cabecalhos,
        json={
            "titulo": "Tarefa para atualizar",
            "concluida": False,
            "prioridade": "low",
        },
    )
    assert criada.status_code == 201
    id_tarefa = criada.json()["id"]

    atualizada = client.patch(
        f"/tarefas/{id_tarefa}",
        headers=cabecalhos,
        json={"concluida": True, "prioridade": "high"},
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["concluida"] is True
    assert atualizada.json()["prioridade"] == "high"

    apagada = client.delete(
        f"/tarefas/{id_tarefa}",
        headers=cabecalhos,
    )
    assert apagada.status_code == 200

    depois = client.get(
        f"/tarefas/{id_tarefa}",
        headers=cabecalhos,
    )
    assert depois.status_code == 404