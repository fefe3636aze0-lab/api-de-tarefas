from pydantic import BaseModel, Field


class NovaTarefa(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    concluida: bool = False
    prioridade: str = "Medium"


class AtualizacaoValor(BaseModel):
    concluida: bool
    prioridade: str


class TarefaResposta(BaseModel):
    id: int
    titulo: str
    concluida: bool
    prioridade: str

class PaginaTarefas(BaseModel):
    itens: list[TarefaResposta]
    total: int
    pagina: int
    limite: int
    tem_proxima: bool

class MensagemResposta(BaseModel):
    mensagem: str
