import os
from secrets import compare_digest
from fastapi import *
import sqlite3
from modelos import *
from banco import *
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


app = FastAPI(
    title="API de Tarefas",
    description="API para criar, consultar, atualizar e apagar tarefas.",
    version="1.0.0",
)
def validar_api_key(x_api_key: str | None = Header(default=None)):
    chave_correta = os.getenv("API_KEY")

    if (
        chave_correta is None
        or x_api_key is None
        or not compare_digest(x_api_key, chave_correta)
    ):
        raise HTTPException(
            status_code=401,
            detail="Chave de API ausente ou inválida",
        )


iniciar_banco()

@app.get("/", tags=["testes"],)
def inicio():
    return {"mensagem": "olá, usuario, qual é seu nome?"}

@app.get("/oi", tags=["testes"],)
def saudar(nome: str = "adicione seu nome"):
    return {"mensagem": f"olá, {nome}!"}

@app.get("/oi/{nome}", tags=["testes"],)
def saudar_nome(nome: str):
    return {"mensagem": f"ola', {nome}"}

@app.get("/dobro/{num}", tags=["testes"],)
def dobro(num: int):
    return num*2

@app.get("/tarefas", response_model=PaginaTarefas, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def listar_tarefas(
    concluida: bool | None = None,
    limite: int = Query(default=20, ge=1, le=100),
    pagina: int = Query(default=1, ge=1),
):
    offset = (pagina - 1) * limite
    with sqlite3.connect(DB_PATH) as conexao:
        conexao.row_factory = sqlite3.Row

        if concluida is None:
            total = conexao.execute(
                "SELECT COUNT(*) FROM tarefas"
            ).fetchone()[0]

            linhas = conexao.execute(
                """
                SELECT id, titulo, concluida, prioridade
                FROM tarefas
                ORDER BY CASE prioridade
                WHEN "High" THEN 1
                WHEN "Medium" THEN 2
                WHEN "Low" THEN 3
                ELSE 4
                END, id
                LIMIT ? OFFSET ?
                """,
                (limite, offset),
            ).fetchall()
        else:
            valor = int(concluida)

            total = conexao.execute(
                "SELECT COUNT(*) FROM tarefas WHERE concluida = ?",
                (valor,),
            ).fetchone()[0]

            linhas = conexao.execute(
                """
                SELECT id, titulo, concluida, prioridade
                FROM tarefas
                WHERE concluida = ?
                ORDER BY CASE prioridade
                WHEN "High" THEN 1
                WHEN "Medium" THEN 2
                WHEN "Low" THEN 3
                ELSE 4
                END, id
                LIMIT ? OFFSET ?
                """,
                (valor, limite, offset),
            ).fetchall()

    itens = [
        {
            "id": linha["id"],
            "titulo": linha["titulo"],
            "concluida": bool(linha["concluida"]),
            "prioridade": linha["prioridade"]
        }
        for linha in linhas
    ]

    return {
        "itens": itens,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "tem_proxima": offset + len(itens) < total,
    }

@app.post("/tarefas", response_model=TarefaResposta, status_code=201, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def adicionar_tarefa(dados: NovaTarefa):
    with sqlite3.connect(DB_PATH) as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO tarefas (titulo, concluida, prioridade)
            VALUES (?, ?, ?)
            """,
            (dados.titulo, int(dados.concluida), dados.prioridade),
        )

        tarefa = {
            "id": cursor.lastrowid,
            "titulo": dados.titulo,
            "concluida": dados.concluida,
            "prioridade": dados.prioridade
        }

    return tarefa

@app.put("/tarefas/{tar_id}", response_model=TarefaResposta, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def atualizar_tarefa(tar_id: int, dados: NovaTarefa):
    with sqlite3.connect(DB_PATH) as conexao:
        cursor = conexao.execute(
            """
            UPDATE tarefas
            SET titulo = ?, concluida = ?, prioridade = ?
            WHERE id = ?
            """,
            (dados.titulo, int(dados.concluida), dados.prioridade, tar_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada",
            )

    return {
        "id": tar_id,
        "titulo": dados.titulo,
        "concluida": dados.concluida,
        "prioridade": dados.prioridade
    }

@app.delete("/tarefas/{tar_id}", response_model=MensagemResposta, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def remove_tarefa(tar_id: int):
    with sqlite3.connect(DB_PATH) as conexao:
        cursor = conexao.execute(
            "DELETE FROM tarefas WHERE id = ?",
            (tar_id,),
        )

        apagou = cursor.rowcount > 0

    if not apagou:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada",
        )

    return {"mensagem": f"Tarefa {tar_id} apagada"}

@app.get("/tarefas/{tar_id}", response_model=TarefaResposta, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def find_id(tar_id: int):
    with sqlite3.connect(DB_PATH) as conexao:
        conexao.row_factory = sqlite3.Row

        cursor = conexao.execute(
            """
            SELECT id, titulo, concluida, prioridade
            FROM tarefas
            WHERE id = ?
            """,
            (tar_id,),
        )

        tarefa = cursor.fetchone()

    if tarefa is None:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada",
        )

    return {
        "id": tarefa["id"],
        "titulo": tarefa["titulo"],
        "concluida": bool(tarefa["concluida"]),
        "prioridade": tarefa["prioridade"]
    }


@app.patch("/tarefas/{tar_id}", response_model=TarefaResposta, dependencies=[Depends(validar_api_key)], tags=["Tarefas"],)
def atualizar_valor(tar_id: int, dados: AtualizacaoValor):
    with sqlite3.connect(DB_PATH) as conexao:
        cursor = conexao.execute(
            "UPDATE tarefas SET concluida = ?, prioridade = ? WHERE id = ?",
            (int(dados.concluida), str(dados.prioridade), tar_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada",
            )

        conexao.row_factory = sqlite3.Row
        tarefa = conexao.execute(
            "SELECT id, titulo, concluida, prioridade FROM tarefas WHERE id = ?",
            (tar_id,),
        ).fetchone()

    return {
        "id": tarefa["id"],
        "titulo": tarefa["titulo"],
        "concluida": bool(tarefa["concluida"]),
        "prioridade": tarefa["prioridade"]
    }


@app.get("/health", tags=["Sistema"],)
def verificar_saude():
    try:
        with sqlite3.connect(DB_PATH, timeout=1) as conexao:
            conexao.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível",
        )

    return {"status": "ok", "database": "ok"}
