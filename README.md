# API de Tarefas

API REST criada com FastAPI e SQLite para cadastrar e gerenciar tarefas. O projeto inclui validação de dados com Pydantic, autenticação por chave de API, filtros, paginação, ordenação por prioridade e testes automatizados.

## Requisitos

- Python 3.10 ou mais recente
- `pip`

## Executar localmente

No PowerShell, dentro desta pasta:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` e defina uma chave privada em `API_KEY`. Depois inicie a API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

A API ficará em `http://127.0.0.1:8000`. A documentação interativa do FastAPI fica em `http://127.0.0.1:8000/docs`.

## Endpoints principais

| Método | Caminho | Ação |
| --- | --- | --- |
| `GET` | `/tarefas` | Lista tarefas; aceita filtros e paginação |
| `GET` | `/tarefas/{id}` | Busca uma tarefa |
| `POST` | `/tarefas` | Cria uma tarefa |
| `PUT` | `/tarefas/{id}` | Substitui os dados editáveis da tarefa |
| `PATCH` | `/tarefas/{id}` | Atualiza conclusão e prioridade |
| `DELETE` | `/tarefas/{id}` | Remove uma tarefa |
| `GET` | `/health` | Verifica se a API e o banco respondem |

As rotas de tarefas exigem o cabeçalho `X-API-Key`, com o valor configurado em `API_KEY`. `/health` e as rotas de demonstração não exigem essa chave.

Exemplo de criação:

```http
POST /tarefas
X-API-Key: sua-chave
Content-Type: application/json

{
  "titulo": "Estudar FastAPI",
  "concluida": false,
  "prioridade": "High"
}
```

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Os testes usam bancos temporários; não precisam acessar o banco de dados local do projeto.

## Estrutura

- `main.py`: inicialização do FastAPI e rotas
- `modelos.py`: modelos e validação dos dados
- `banco.py`: configuração e criação do banco SQLite
- `tests/`: testes automatizados
- `.env.example`: exemplo de configuração local, sem segredo real

O arquivo `.env` e o banco SQLite local são ignorados pelo Git para evitar publicar credenciais ou dados locais.
