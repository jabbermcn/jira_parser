from pathlib import Path

from pydantic import PostgresDsn, HttpUrl, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jira_client import JiraClient


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        frozen=True,
        env_file=".env"
    )

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    HOST: str = "0.0.0.0"
    PORT: int = 80
    WORKERS: int = 1

    POSTGRES_URL: PostgresDsn
    JIRA_DOMAIN: HttpUrl
    JIRA_EMAIL: EmailStr
    JIRA_TOKEN: SecretStr


settings = Settings()

engine = create_engine(url=settings.POSTGRES_URL.unicode_string(), pool_size=50, max_overflow=50)
session_maker = sessionmaker(bind=engine)


jira_client = JiraClient(
    base_url=settings.JIRA_DOMAIN.unicode_string(),
    email=settings.JIRA_EMAIL,
    token=settings.JIRA_TOKEN.get_secret_value()
)
