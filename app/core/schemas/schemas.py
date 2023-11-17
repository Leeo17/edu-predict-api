from datetime import datetime

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
    email: str
    nome: str
    sobrenome: str
    email_verificado: bool
    data_cadastro: datetime


class Token(BaseModel):
    access_token: str
    user: Usuario


class TokenData(BaseModel):
    email: str or None = None


class EmailInput(BaseModel):
    email: str
