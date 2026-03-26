from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    OWEN_LOGIN: str
    OWEN_PASSWORD: str
    OWEN_PARAMETER_ID: int
    

    class Config:
        env_file = ".env"

settings = Settings()