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
    data_ingresso: str  # YYYY-MM-DD
    data_conclusao: str  # YYYY-MM-DD
    curso: int  # id do curso
    curso_contagem_disciplinas: int
    curso_contagem_horas: int
    contagem_disciplinas_cursadas: int
    contagem_horas_cursadas: int
    contagem_reprovacoes: int
    renda_mensal: str  # RENDA_FAMILIAR_OPTIONS
    cor_raca: str  # COR_RACA_OPTIONS
    cota_sisu: str  # COTA_SISU_OPTIONS
    atividade_remunerada: str  # ATIVIDADE_REMUNERADA_OPTIONS
    idade_atividade_remunerada: str  # IDADE_ATIVIDADE_REMUNERADA_OPTIONS
    estudos: str  # ESTUDOS_OPTIONS
    lingua_estrangeira: str  # LINGUA_ESTRANGEIRA_OPTIONS
    principal_fator: str  # FATORES_OPTIONS
    trabalhar_curso: str  # TRABALHO_OPTIONS
    ano_conclusao_ensino_medio: int  # YYYY mínimo de 1989 e máximo de 2019
    turno_ensino_medio: str  # TURNO_ENSINO_MEDIO_OPTIONS
    tipo_ensino_medio: str  # TIPO_ENSINO_MEDIO_OPTIONS
    comunidade_quilombola: str  # SIM_NAO_OPTIONS
    tempo_cursinho: str  # CURSINHO_OPTIONS
    ocupacao_mae: str  # OCUPACAO_MAE_OPTIONS
    ocupacao_pai: str  # OCUPACAO_PAI_OPTIONS
    situacao_moradia: str  # SITUACAO_MORADIA_OPTIONS
    estado_nascimento: str  # ESTADO_NASCIMENTO_OPTIONS
    local_residencia: str  # LOCAL_RESIDENCIA_OPTIONS
    motivo_curso: str  # MOTIVO_CURSO_OPTIONS
    instrucao_mae: str  # NIVEL_INSTRUCAO_OPTIONS
    instrucao_pai: str  # NIVEL_INSTRUCAO_OPTIONS
    estado_civil: str  # ESTADO_CIVIL_OPTIONS
    sexo: str  # SEXO_OPTIONS
    participacao_economica: str  # PARTICIPACAO_FAMILIAR_OPTIONS
    contribuintes_renda_familiar: int
    sustentadas_renda_familiar: int
    escolha_curso: str  # ESCOLHA_CURSO_OPTIONS
    recursos_escolha_curso: str  # RECURSOS_ESCOLHA_CURSO_OPTIONS
    influencias_escolha_curso: str  # INFLUENCIA_ESCOLHA_CURSO_OPTIONS
    razao_novo_processo_seletivo: str  # NOVO_PROCESSO_SELETIVO_OPTIONS
    etnia_indigena: str  # INDIGENA_OPTIONS
    necessidade_especial: str  # NECESSIDADE_ESPECIAL_OPTIONS
    tipo_necessidade_especial: str  # TIPO_NECESSIDADE_ESPECIAL_OPTIONS
    vestibular_outros_anos: str  # VESTIBULAR_OUTROS_ANOS_OPTIONS
    iniciou_curso_superior: str  # INICIO_CURSO_SUPERIOR_OPTIONS
