from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine
from settings import ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.get_current_user(db, token)


@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
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


@app.get("/user", response_model=schemas.UsuarioResponse)
async def show_current_user(
    current_user: schemas.Usuario = Depends(current_user),
):
    return current_user


@app.post("/user/", response_model=schemas.UsuarioResponse)
async def create_user(
    user: schemas.UsuarioInput,
    db: Session = Depends(get_db),
    current_user: schemas.Usuario = Depends(current_user),
):
    return crud.create_user(db, user, current_user.email)
