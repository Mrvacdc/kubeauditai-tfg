from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service="kubeaudit-api",
        version="0.1.0",
        environment=settings.APP_ENV,
    )


@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """
    Valida conectividad básica contra PostgreSQL.
    """
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "reachable",
    }
