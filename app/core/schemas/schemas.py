from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UsuarioInput(BaseModel):
    email: str
    nome: str
    sobrenome: str


class UsuarioPassInput(BaseModel):
    senha: str
    confirmar_senha: str
    codigo_verificacao: str


class Usuario(BaseModel):
    id: UUID
    email: str
    nome: str
    sobrenome: str
    email_verificado: bool
    data_cadastro: datetime


class Analise(BaseModel):
    id: UUID
    id_usuario: UUID
    indice_potencial_evasao: float
    data: datetime


class Token(BaseModel):
    access_token: str
    user: Usuario


class TokenData(BaseModel):
    email: str or None = None


class EmailInput(BaseModel):
    email: str


class Curso(BaseModel):
    id: int
    nome: str
