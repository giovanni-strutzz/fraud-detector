from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import settings
from src.infrastructure.http.routers import router as transfers_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Motor de Transferencias utilizando Arquitetura Hexagonal, CQRS e Event Sourcing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(transfers_router)


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "UP",
        "service": "fintech-core-service",
        "message": "Healthy"
    }