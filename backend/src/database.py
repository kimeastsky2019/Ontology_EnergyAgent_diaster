"""Database configuration"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

from src.config import settings

# Create async database engine
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
# SQLite인 경우 pool_size를 사용하지 않음
if "sqlite" in database_url.lower():
    async_engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False} if "sqlite" in database_url.lower() else {},
    )
else:
    async_engine = create_async_engine(
        database_url,
        pool_size=settings.DATABASE_POOL_SIZE,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

# Create sync database engine (for migrations)
# SQLite인 경우 pool_size를 사용하지 않음
if "sqlite" in settings.DATABASE_URL.lower():
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency to get async database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency to get sync database session (for migrations)
def get_sync_db():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




