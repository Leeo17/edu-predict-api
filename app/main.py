import json
from datetime import timedelta

import aiohttp
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import event
from sqlalchemy.orm import Session

import app.core.models.models as models
import app.core.schemas.schemas as schemas
import app.core.utils.analysis as analysis_service
import app.core.utils.courses as courses
import app.core.utils.user as user_service
from app.core.models.database import Base, db_session, engine, get_db
from app.core.settings import settings

app = FastAPI()
analysis_form = '{"RENDA_FAMILIAR_OPTIONS":"De R$ 1448,01 até R$ 1634,00", "COR_RACA_OPTIONS":"Branca", "COTA_SISU_OPTIONS":"Independente da renda + ensino médio", "ATIVIDADE_REMUNERADA_OPTIONS":"Sim - meio período", "IDADE_ATIVIDADE_REMUNERADA_OPTIONS":"Depois dos 16", "ESTUDOS_OPTIONS":"Integralmente em escola particular", "LINGUA_ESTRANGEIRA_OPTIONS":"Leio apenas uma outra Língua Estrangeira", "FATORES_OPTIONS":"Persistência e hábitos de estudo", "TRABALHO_OPTIONS":"Sim, desde o primeiro ano, em tempo integral", "TURNO_ENSINO_MEDIO_OPTIONS":"Maior parte diurno", "TIPO_ENSINO_MEDIO_OPTIONS":"Ensino médio regular", "SIM_NAO_OPTIONS":"Sim", "CURSINHO_OPTIONS":"Não fiz cursinho", "OCUPACAO_MAE_OPTIONS":"Sócia ou proprietária de empresa", "OCUPACAO_PAI_OPTIONS":"Parlamentar ou cargo eleitoral, diplomata, militar", "SITUACAO_MORADIA_OPTIONS":"Mora em república, casa de estudante, pensão ou pensionato", "ESTADO_NASCIMENTO_OPTIONS":"Paraná", "LOCAL_RESIDENCIA_OPTIONS":"Curitiba", "MOTIVO_CURSO_OPTIONS":"Permite conciliar aula e trabalho", "NIVEL_INSTRUCAO_OPTIONS":"Sem escolaridade", "ESTADO_CIVIL_OPTIONS":"Casado(a)", "SEXO_OPTIONS":"Masculino", "PARTICIPACAO_FAMILIAR_OPTIONS":"Trabalho e contribuo em parte para o sustento da família", "ESCOLHA_CURSO_OPTIONS":"Muito indeciso (entre a opção que fez e várias outras)", "RECURSOS_ESCOLHA_CURSO_OPTIONS":"Conversas com professores", "INFLUENCIA_ESCOLHA_CURSO_OPTIONS":"Profissionais da área", "NOVO_PROCESSO_SELETIVO_OPTIONS":"Por desejar outra formação", "INDIGENA_OPTIONS":"Tupi Guarani", "NECESSIDADE_ESPECIAL_OPTIONS":"Sim", "TIPO_NECESSIDADE_ESPECIAL_OPTIONS":"Transtorno do Espectro do Autismo", "VESTIBULAR_OUTROS_ANOS_OPTIONS":"Sim, este é o segundo ano que faço vestibular", "INICIO_CURSO_SUPERIOR_OPTIONS":"Sim, estou cursando"}'

origins = ["http://localhost:4200", settings.APP_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database initial data
INITIAL_DATA = {
    "usuarios": [
        {
            "email": "admin@ufpr.br",
            "nome": "Administrador",
            "sobrenome": "Admin",
            "senha": user_service.get_password_hash("123qweadmin"),
            "email_verificado": True,
        },
    ],
}


# This method receives a table, a connection and inserts data to that table.
def initialize_table(target, connection, **kw):
    tablename = str(target)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])


event.listen(models.Usuario.__table__, "after_create", initialize_table)

Base.metadata.create_all(bind=engine)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    db_session.set(db)
    return user_service.get_current_user(token)


def count_filled_properties(analise_input: schemas.AnaliseInput) -> bool:
    count = 0
    for value in analise_input.model_dump().values():
        if value != 0 and value != "":
            count += 1
    return count >= 15


@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_session.set(db)

    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "user": user}


@app.get("/user", response_model=schemas.Usuario)
async def show_current_user(
    current_user: schemas.Usuario = Depends(get_current_user),
):
    return current_user


@app.post("/user", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UsuarioInput,
    current_user: schemas.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_session.set(db)

    return await user_service.create_user(user, current_user.email)


@app.post("/user/password")
async def create_user_password(
    password_input: schemas.UsuarioPassInput,
    db: Session = Depends(get_db),
):
    db_session.set(db)

    return user_service.create_user_password(password_input)


@app.post("/user/password/email")
async def send_reset_password_email(
    email_input: schemas.EmailInput,
    db: Session = Depends(get_db),
):
    db_session.set(db)

    return await user_service.send_reset_password_email(email_input.email)


@app.get("/analyses", response_model=list[schemas.Analise])
async def get_all_user_analyses(
    current_user: schemas.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_session.set(db)
    return analysis_service.get_all_user_analyses(current_user)


@app.get("/analysis/courses", response_model=list[schemas.Curso])
async def get_courses(course_filter: str = ""):
    return courses.get_courses(course_filter)


@app.delete("/analysis/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_analysis(
    analysis_id: str,
    current_user: schemas.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_session.set(db)

    analysis_service.delete_user_analysis(analysis_id, current_user.id)


@app.post("/analysis")
async def new_analysis(
    analise_input: schemas.AnaliseInput,
    db: Session = Depends(get_db),
):
    db_session.set(db)

    if not count_filled_properties(analise_input):
        raise HTTPException(
            status_code=400, detail="Ao menos 15 campos devem ser preenchidos."
        )

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            settings.MODEL_URL, json=json.loads(analysis_form), ssl=False
        )
        return await response.json()
