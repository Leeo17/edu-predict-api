from datetime import timedelta

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


@app.post("/analysis", response_model=schemas.Analise)
async def new_analysis(
    analise_input: schemas.AnaliseInput,
    current_user: schemas.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_session.set(db)

    if not count_filled_properties(analise_input):
        raise HTTPException(
            status_code=400, detail="Ao menos 15 campos devem ser preenchidos."
        )

    return analysis_service.create_analysis(analise_input, current_user)
