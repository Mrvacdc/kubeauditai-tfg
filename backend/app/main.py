import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "API para gestión de auditorías de cumplimiento CIS Benchmark "
            "en clústeres Kubernetes."
        ),
        version="0.1.0",
        debug=settings.APP_DEBUG,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handler genérico.

        En producción se debe evitar devolver detalles internos del error.
        """
        logger.exception("Unhandled application error")

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "path": str(request.url.path),
            },
        )

    return app


app = create_app()
