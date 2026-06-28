import logging

from app.core.config import get_settings


def configure_logging() -> None:
    """
    Configura el logging base de la aplicación.

    En fases posteriores se debe evitar registrar tokens, kubeconfigs,
    certificados, passwords o cualquier dato sensible.
    """
    settings = get_settings()

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
