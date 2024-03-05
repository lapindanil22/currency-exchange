from typing import AsyncGenerator
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

Base = declarative_base()

# DATABASE_URL = "sqlite:///./database.db"
# engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# async_session_maker = async_sessionmaker(engine, autoflush=False)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
