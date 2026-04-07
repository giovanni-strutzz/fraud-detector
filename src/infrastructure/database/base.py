from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, DateTime, func
from pgvector.sqlalchemy import Vector
from src.infrastructure.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class AccountModel(Base):
    __tablename__ = "accounts"

    account_id = Column(String, primary_key=True, index=True)
    document = Column(String, index=True)
    balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    transaction_behavior_embedding = Column(Vector(3), nullable=False)