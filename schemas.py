from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str or None = None


class UsuarioInput(BaseModel):
    email: str
    nome_completo: str
    senha: str


class Usuario(UsuarioInput):
    email_confirmado: bool
    desabilitado: bool
    data_cadastro: datetime


class UsuarioResponse(BaseModel):
    email: str
    nome_completo: str
    email_confirmado: bool
    desabilitado: bool
    data_cadastro: datetime
