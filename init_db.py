import asyncio
from sqlalchemy import text
from src.infrastructure.database.base import Base, engine
from src.infrastructure.config import settings

async def init_models():
    async with engine.begin() as conn:
        print("Ativando extensão pgvector no PostgreSQL...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        print("Criando tabelas...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_models())