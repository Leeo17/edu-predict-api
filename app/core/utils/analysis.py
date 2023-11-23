import app.core.models.models as models
import app.core.schemas.schemas as schemas
from app.core.models.database import db_session


def get_all_user_analysis(user: schemas.Usuario):
    db_context = db_session.get()
    return (
        db_context.query(models.Analise)
        .filter(models.Analise.id_usuario == user.id)
        .all()
    )
