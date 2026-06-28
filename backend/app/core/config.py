from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración principal de KubeAudit.

    Los valores se cargan desde variables de entorno o desde un archivo .env.
    No se deben almacenar secretos reales en el repositorio.
    """

    APP_NAME: str = "KubeAudit"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api"

    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = (
        "postgresql+psycopg2://kubeaudit_user:kubeaudit_password@localhost:5432/kubeaudit"
    )

    CORS_ORIGINS: str = "http://localhost:5173,https://kubeauditai.marcosvillegas.dev"

    KUBERNETES_CONNECTION_MODE: str = "kubeconfig"
    KUBECONFIG_PATH: str = "/opt/kubeaudit/kubeconfigs/demo-cluster.kubeconfig"

    KUBE_BENCH_IMAGE: str = "aquasec/kube-bench:v0.15.6"
    KUBE_BENCH_NAMESPACE: str = "kubeaudit-system"
    KUBE_BENCH_JOB_TIMEOUT_SECONDS: int = 180
    KUBE_BENCH_CLEANUP_JOB: bool = True

    AI_PROVIDER: str = "rule_engine"

    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    RECOMMENDATION_SOURCE: str = "deepseek"

    AI_RECOMMENDATION_TEMPERATURE: float = 0.2
    AI_RECOMMENDATION_MAX_TOKENS: int = 2000
    AI_API_KEY: str = "change-me"
    AI_MODEL: str = "change-me"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convierte la variable CORS_ORIGINS en una lista compatible con FastAPI.
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = Settings()
