import hashlib
from datetime import datetime, timedelta
from random import randbytes

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

import app.core.models.models as models
import app.core.schemas.schemas as schemas
from app.core.models.database import db_session
from app.core.settings import settings
from app.core.utils.mailer import Email

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


def check_if_user_is_verified(user: models.Usuario):
    if not user.email_verificado:
        raise HTTPException(status_code=400, detail="Email não verificado")


async def create_user(user: schemas.UsuarioInput, creator_email: str or None = None):
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

    # Check if the first and last name have at least 2 characters
    if len(user.nome) < 2 or len(user.sobrenome) < 2:
        raise HTTPException(
            status_code=400,
            detail="O nome e sobrenome devem ter pelo menos 2 caracteres",
        )

    # Create user on database
    try:
        token = randbytes(10)
        hashed_code = hashlib.sha256()
        hashed_code.update(token)
        verification_code = hashed_code.hexdigest()

        db_user = models.Usuario(
            email=user.email,
            nome=user.nome,
            sobrenome=user.sobrenome,
            codigo_verificacao=verification_code,
            criado_por=creator_email,
        )

        db_context.add(db_user)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro ao tentar adicionar o usuário na database: {str(e.orig)}",
        )

    # Send verification email
    try:
        url = f"{settings.APP_URL}/auth/set-password?code={token.hex()}"
        await Email(user.nome, url, [user.email]).send_mail(
            "Complete seu cadastro no Edu Predict", "verification"
        )
    except Exception as error:
        db_context.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao enviar o email de verificação: {str(error)}",
        )

    db_context.commit()
    db_context.refresh(db_user)
    return schemas.Usuario(**db_user.__dict__)


def get_current_user(token: str):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception

        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credential_exception

    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credential_exception

    check_if_user_is_verified(user)

    return user


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email=email)
    if not user:
        return False

    check_if_user_is_verified(user)

    if not verify_password(password, user.senha):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_user_password(password_input: schemas.UsuarioPassInput):
    db_context = db_session.get()

    # Check if the password has at least 6 characters
    if len(password_input.senha) < 6:
        raise HTTPException(
            status_code=400, detail="A senha deve ter pelo menos 6 caracteres"
        )

    # Check if the password matches the confirmation
    if password_input.senha != password_input.confirmar_senha:
        raise HTTPException(status_code=400, detail="As senhas não correspondem")

    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(password_input.codigo_verificacao))
    verification_code = hashedCode.hexdigest()

    user = (
        db_context.query(models.Usuario)
        .filter(models.Usuario.codigo_verificacao == verification_code)
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Código de verificação inválido")

    hashed_password = get_password_hash(password_input.senha)

    user.senha = hashed_password
    user.email_verificado = True
    user.codigo_verificacao = None
    user.data_verificacao = datetime.utcnow()

    db_context.commit()
    db_context.refresh(user)

    return True


async def send_reset_password_email(email: str):
    db_context = db_session.get()

    user = (
        db_context.query(models.Usuario).filter(models.Usuario.email == email).first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Email não cadastrado")

    token = randbytes(10)
    hashed_code = hashlib.sha256()
    hashed_code.update(token)
    verification_code = hashed_code.hexdigest()

    user.codigo_verificacao = verification_code

    # Send verification email
    try:
        url = f"{settings.APP_URL}/auth/set-password?code={token.hex()}"
        await Email(user.nome, url, [user.email]).send_mail(
            "Recuperação de senha do Edu Predict", "reset"
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao enviar o email de verificação: {str(error)}",
        )

    db_context.commit()
    db_context.refresh(user)

    return True
