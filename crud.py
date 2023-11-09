from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

import models
import schemas
from database import db_session
from settings import ALGORITHM, SECRET_KEY

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(email: str):
    db_context = db_session.get()
    return (
        db_context.query(models.Usuario).filter(models.Usuario.email == email).first()
    )


def verify_password(plain_password, hashed_password):
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)


def verify_user(user: models.Usuario):
    if not user.email_verificado:
        raise HTTPException(status_code=400, detail="Email não verificado")

    if not user.usuario_ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")


def create_user(user: schemas.UsuarioInput, creator_email: str or None = None):
    db_context = db_session.get()
    # Check if the email belongs to the UFPR domain
    domain = "ufpr.br"
    if not user.email.endswith(f"@{domain}"):
        raise HTTPException(
            status_code=400, detail="O email deve terminar com @ufpr.br"
        )

    # Check if the email is already registered
    db_user = (
        db_context.query(models.Usuario)
        .filter(models.Usuario.email == user.email)
        .first()
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
        criado_por=creator_email,
    )

    try:
        db_context.add(db_user)
        db_context.commit()
        db_context.refresh(db_user)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error when adding the user to the database: {str(e.orig)}",
        )

    return schemas.Usuario(**db_user.__dict__)


def get_current_user(token: str):
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

        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credential_exception

    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credential_exception

    verify_user(user)

    return user


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email=email)
    verify_user(user)
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
