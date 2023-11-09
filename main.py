from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import event
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, db_session, engine, get_db
from settings import ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database initial data
INITIAL_DATA = {
    "usuarios": [
        {
            "email": "admin@ufpr.br",
            "nome_completo": "Administrador",
            "senha": crud.get_password_hash("123qweadmin"),
            "email_verificado": True,
            "usuario_ativo": True,
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


def current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_session.set(db)
    return crud.get_current_user(token)


@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_session.set(db)

    user = crud.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user", response_model=schemas.Usuario)
async def show_current_user(
    current_user: schemas.Usuario = Depends(current_user),
):
    return current_user


@app.post("/user/", response_model=schemas.Usuario)
async def create_user(
    user: schemas.UsuarioInput,
    current_user: schemas.Usuario = Depends(current_user),
    db: Session = Depends(get_db),
):
    db_session.set(db)

    return crud.create_user(user, current_user.email)
