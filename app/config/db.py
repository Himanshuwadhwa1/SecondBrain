from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.env import DATABASE_URL
from app.util.db import _parse_db_url

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def ensure_database_exists(database_url: str) -> None:
    admin_url, db_name = _parse_db_url(database_url)
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        )
        if result.scalar() is None:
            await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    await engine.dispose()

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_database_exists(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Startup complete: Tables created")
    
    yield
    
    await engine.dispose()
    print("Shutdown complete: Engine disposed")