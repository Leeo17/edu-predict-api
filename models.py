import uuid
from datetime import datetime

from sqlalchemy import JSON, UUID, Boolean, Column, DateTime, ForeignKey, String

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    email_verificado = Column(Boolean, default=False, nullable=False)
    usuario_ativo = Column(Boolean, default=False, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    criado_por = Column(String)


class Analise(Base):
    __tablename__ = "analises"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    resultado = Column(JSON, nullable=False)
    data = Column(DateTime, default=datetime.utcnow, nullable=False)
