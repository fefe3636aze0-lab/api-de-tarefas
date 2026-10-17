import os
import requests
from dotenv import load_dotenv

load_dotenv()

chave = os.getenv("API_KEY")

resposta = requests.post(
    "http://127.0.0.1:8000/tarefas",
    headers={"X-API-Key": chave},
    json={
        "titulo": "banana",
        "concluida": False,
        "prioridade": "Low"
    }

)

print(resposta.status_code)
print(resposta.json())