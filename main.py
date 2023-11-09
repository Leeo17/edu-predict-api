from contextvars import ContextVar
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session: ContextVar[Session] = ContextVar("db_session")


def verify_password(plain_password, hashed_password):
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)


def get_user(email: str):
    db = db_session.get()

    db_user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    user = Usuario(
        email=db_user.email,
        nome_completo=db_user.nome_completo,
        senha=db_user.senha,
        email_confirmado=db_user.email_confirmado,
        desabilitado=db_user.desabilitado,
        data_cadastro=db_user.data_cadastro,
    )
    return user


def authenticate_user(email: str, password: str):
    user = get_user(email=email)
    if not user:
        return False
    if not verify_password(password, user.senha):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    current_user = await get_user_by_token(token)
    return current_user


async def get_user_by_token(token: str):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception

        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception

    user = get_user(email=token_data.email)
    if user is None:
        raise credential_exception

    if user.disabled:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    return user


@app.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_session.set(db)

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @app.get("/user", response_model=Usuario)
# async def show_current_user(
#     current_user: Usuario = Depends(get_current_user),
# ):
#     return current_user


@app.post("/user/", response_model=Usuario)
async def create_user(
    user: UsuarioInput,
    db: Session = Depends(get_db),
):
    db_session.set(db)

    # Check if the email belongs to the UFPR domain
    domain = "ufpr.br"
    if not user.email.endswith(f"@{domain}"):
        raise HTTPException(
            status_code=400, detail="O email deve terminar com @ufpr.br"
        )

    # Check if the email is already registered
    db_user = (
        db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    )
    if db_user:
        raise HTTPException(
            status_code=400, detail="O email já está cadastrado no sistema"
        )

    # Check if the password has at least 6 characters
    if len(user.senha) < 6:
        raise HTTPException(
            status_code=400, detail="A senha deve ter pelo menos 6 caracteres"
        )

    db_user = models.Usuario(
        email=user.email,
        nome_completo=user.nome_completo,
        senha=get_password_hash(user.senha),
        criado_por=None,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error when adding the user to the database: {str(e.orig)}",
        )

    return db_user
