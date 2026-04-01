from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _database_url() -> str:
    if settings.DATABASE_URL:
        url = settings.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://") :]
        return url
    return (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@localhost:{settings.DB_PORT}/{settings.DB_NAME}"
    )


engine = create_engine(_database_url())

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)