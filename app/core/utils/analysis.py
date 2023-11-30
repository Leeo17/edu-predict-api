import random
from datetime import datetime

from fastapi import HTTPException

import app.core.models.models as models
import app.core.schemas.schemas as schemas
from app.core.models.database import db_session


def get_all_user_analyses(user: schemas.Usuario):
    db_context = db_session.get()
    return (
        db_context.query(models.Analise)
        .filter(models.Analise.id_usuario == user.id)
        .order_by(models.Analise.data.desc())
        .all()
    )


def delete_user_analysis(analysis_id: str, user_id: str):
    db_context = db_session.get()
    db_analysis = (
        db_context.query(models.Analise)
        .filter(models.Analise.id_usuario == user_id, models.Analise.id == analysis_id)
        .first()
    )
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    db_context.delete(db_analysis)
    db_context.commit()


def create_analysis(analysis: schemas.AnaliseInput, user: schemas.Usuario):
    db_context = db_session.get()
    db_analysis = models.Analise(
        id_usuario=user.id,
        indice_potencial_evasao=round(random.uniform(0, 1), 3),
        data=datetime.utcnow(),
    )
    db_context.add(db_analysis)
    db_context.commit()
    db_context.refresh(db_analysis)

    return db_analysis
