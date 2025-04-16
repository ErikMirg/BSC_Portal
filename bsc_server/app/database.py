from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings


DATABASE_URL = settings.DATABASE_URL.replace("psycopg2", "asyncpg")

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"server_settings": {"timezone": "utc"}}
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session