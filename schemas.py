from datetime import datetime

from pydantic import BaseModel


class UsuarioInput(BaseModel):
    email: str
    nome: str
    sobrenome: str
    senha: str
    confirmar_senha: str


class Usuario(BaseModel):
    email: str
    nome: str
    sobrenome: str
    email_verificado: bool
    usuario_ativo: bool
    data_cadastro: datetime


class Token(BaseModel):
    access_token: str
    user: Usuario


class TokenData(BaseModel):
    email: str or None = None
