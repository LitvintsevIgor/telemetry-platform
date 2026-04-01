from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """DB: set DATABASE_URL (production) or DB_* + localhost (local)."""

    DATABASE_URL: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    OWEN_PARAMETER_ID: int
    # Comma-separated origins for browser clients (e.g. http://localhost:5173,https://app.example.com)
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @model_validator(mode="after")
    def require_db_config(self):
        if self.DATABASE_URL:
            return self
        if any(
            x is None
            for x in (self.DB_PORT, self.DB_NAME, self.DB_USER, self.DB_PASSWORD)
        ):
            raise ValueError(
                "Set DATABASE_URL or all of DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
            )
        return self


settings = Settings()