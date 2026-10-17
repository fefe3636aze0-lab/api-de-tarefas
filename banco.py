import os
from pathlib import Path
import sqlite3

DATA_DIR = Path(
    os.getenv("DATA_DIR", str(Path(__file__).resolve().parent))
)
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "tarefas.db"

def iniciar_banco():
    with sqlite3.connect(DB_PATH) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                concluida INTEGER NOT NULL DEFAULT 0,
                prioridade TEXT NOT NULL
            )
        """)