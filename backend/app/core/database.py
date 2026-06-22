from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Adjust the connection string for asyncpg if it starts with postgresql:// or postgres://
db_url = settings.DATABASE_URL
if db_url:
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Debugging: Log the URL prefix (safe for production)
    print(f"DATABASE_URL configured with prefix: {db_url.split(':', 1)[0]}...")

engine = None
async_session = None

import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

if db_url:
    engine = create_async_engine(
        db_url,
        connect_args={
            "ssl": ssl_context,
            "statement_cache_size": 0
        },
        echo=False
    )
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

Base = declarative_base()

async def get_db():
    if not async_session:
        print("CRITICAL: async_session is None")
        raise RuntimeError("Database URL not configured")
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {str(e)}")
        raise
