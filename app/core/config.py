"""환경변수 기반 애플리케이션 설정을 정의한다."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """`.env` 또는 실행 환경에서 읽어 오는 필수 설정값 모음."""

    env: str
    api_host: str
    api_port: int
    tourapi_db_path: Path
    cors_origins: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """환경변수를 검증하고 타입이 적용된 설정 객체를 반환한다."""
    return Settings()
