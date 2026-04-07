# FraudDetector

Projeto FastAPI seguindo **Arquitetura Hexagonal** (Ports & Adapters).

## Estrutura

```
src/
├── domain/               # Núcleo — zero dependências externas
│   └── <dominio>/
│       ├── entities/     # Entidades e Value Objects
│       ├── ports/        # Interfaces (contratos)
│       └── services/     # Regras de negócio
│
├── application/          # Casos de uso orquestrados (opcional)
│
└── infrastructure/       # Adaptadores (HTTP, DB, serviços externos)
    ├── config.py
    ├── database/         # SQLAlchemy models + repositórios concretos
    └── http/             # FastAPI routers + schemas Pydantic
```

## Regra de dependência

```
Infrastructure → Application → Domain
```

O **Domain nunca importa** camadas externas.

## Instalação

```bash
poetry install
cp .env.example .env
uvicorn src.main:app --reload
```

## Testes

```bash
pytest
```
