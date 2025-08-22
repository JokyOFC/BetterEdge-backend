from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
