from fastapi import APIRouter

from app.api import audit_logs
from app.api import auth
from app.api import clusters
from app.api import audits
from app.api import findings
from app.api import recommendations
from app.api import dashboard
from app.api import health
from app.api import reports

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(clusters.router)
api_router.include_router(audits.router)
api_router.include_router(findings.router)
api_router.include_router(recommendations.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(audit_logs.router)