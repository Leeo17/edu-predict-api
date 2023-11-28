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
    dataIngresso: str
    dataConclusao: str
    curso: int
    cursoContagemDisciplinas: int
    cursoContagemHoras: int
    contagemDisciplinasCursadas: int
    contagemHorasCursadas: int
    contagemReprovacoes: int
    rendaMensal: str
    corRaca: str
    cotaSisu: str
    atividadeRemunerada: str
    idadeAtividadeRemunerada: str
    estudos: str
    linguaEstrangeira: str
    principalFator: str
    trabalharCurso: str
    anoConclusaoEnsinoMedio: int
    turnoEnsinoMedio: str
    tipoEnsinoMedio: str
    comunidadeQuilombola: str
    tempoCursinho: str
    ocupacaoMae: str
    ocupacaoPai: str
    situacaoMoradia: str
    estadoNascimento: str
    localResidencia: str
    motivoCurso: str
    instrucaoMae: str
    instrucaoPai: str
    estadoCivil: str
    sexo: str
    participacaoEconomica: str
    contribuintesRendaFamiliar: int
    sustentadasRendaFamiliar: int
    escolhaCurso: str
    recursosEscolhaCurso: str
    influenciasEscolhaCurso: str
    razaoNovoProcessoSeletivo: str
    etniaIndigena: str
    necessidadeEspecial: str
    tipoNecessidadeEspecial: str
    vestibularOutrosAnos: str
    iniciouCursoSuperior: str
