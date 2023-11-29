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


class AnaliseInput(BaseModel):
    data_ingresso: str
    data_conclusao: str
    curso: int
    curso_contagem_disciplinas: int
    curso_contagem_horas: int
    contagem_disciplinas_cursadas: int
    contagem_horas_cursadas: int
    contagem_reprovacoes: int
    renda_mensal: str
    cor_raca: str
    cota_sisu: str
    atividade_remunerada: str
    idade_atividade_remunerada: str
    estudos: str
    lingua_estrangeira: str
    principal_fator: str
    trabalhar_curso: str
    ano_conclusao_ensino_medio: int
    turno_ensino_medio: str
    tipo_ensino_medio: str
    comunidade_quilombola: str
    tempo_cursinho: str
    ocupacao_mae: str
    ocupacao_pai: str
    situacao_moradia: str
    estado_nascimento: str
    local_residencia: str
    motivo_curso: str
    instrucao_mae: str
    instrucao_pai: str
    estado_civil: str
    sexo: str
    participacao_economica: str
    contribuintes_renda_familiar: int
    sustentadas_renda_familiar: int
    escolha_curso: str
    recursos_escolha_curso: str
    influencias_escolha_curso: str
    razao_novo_processo_seletivo: str
    etnia_indigena: str
    necessidade_especial: str
    tipo_necessidade_especial: str
    vestibular_outros_anos: str
    iniciou_curso_superior: str
