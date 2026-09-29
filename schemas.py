from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UsuarioCriacao(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    cargo: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor):
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("Senha excede o limite suportado pelo algoritmo de hash")
        return valor

    @field_validator("nome", "cargo")
    @classmethod
    def validar_texto(cls, valor):
        valor = " ".join(valor.split())
        if len(valor) < 2:
            raise ValueError("Campo obrigatório")
        return valor

class LoginDados(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)

class CampeonatoCriacao(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    temporada: str = Field(min_length=1, max_length=30)

    @field_validator("nome", "temporada")
    @classmethod
    def validar_texto(cls, valor):
        valor = " ".join(valor.split())
        if not valor:
            raise ValueError("Campo obrigatório")
        return valor

class PartidaCriacao(BaseModel):
    campeonato_id: int = Field(gt=0)
    data_partida: date
    adversario: str = Field(min_length=2, max_length=150)

    @field_validator("adversario")
    @classmethod
    def validar_adversario(cls, valor):
        valor = " ".join(valor.split())
        if len(valor) < 2:
            raise ValueError("Adversário inválido")
        return valor

class AtletaCriacao(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    data_nascimento: date
    posicao: str = Field(min_length=2, max_length=50)
    clube_atual: str = Field(min_length=2, max_length=150)

    @field_validator("nome", "posicao", "clube_atual")
    @classmethod
    def validar_texto(cls, valor):
        valor = " ".join(valor.split())
        if len(valor) < 2:
            raise ValueError("Campo obrigatório")
        return valor

    @field_validator("data_nascimento")
    @classmethod
    def validar_nascimento(cls, valor):
        if valor >= date.today():
            raise ValueError("Data de nascimento deve ser anterior a hoje")
        return valor

class Mensagem(BaseModel):
    mensagem: str

class RespostaBase(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
