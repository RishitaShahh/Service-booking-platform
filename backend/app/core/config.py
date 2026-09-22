"""Application configuration module using Pydantic Settings."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class holding configuration values.

    Attributes:
        PROJECT_NAME (str): Title of the API project.
        VERSION (str): Current application version.
        API_V1_STR (str): API prefix path.
        SECRET_KEY (str): Secret key for JWT token generation and validation.
        ALGORITHM (str): Encryption algorithm for JWT tokens.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Expiration time in minutes for access tokens.
        DATABASE_URL (str): Connection string for the database (PostgreSQL/SQLite).
        CORS_ORIGINS (List[str]): List of allowed origins for Cross-Origin Resource Sharing.
    """

    PROJECT_NAME: str = "Service Booking Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey_change_in_production_environment_123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite+aiosqlite:///./service_booking.db"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated CORS origins string into a list of strings.

        Args:
            v (Union[str, List[str]]): Raw CORS origin input.

        Returns:
            List[str]: Parsed list of CORS origins.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
