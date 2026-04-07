from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fintech Core Service"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TRANSFERS: str = "requested_transfers"

    #Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    #PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detector"

    class Config:
        env_file = ".env"

settings = Settings()