import asyncio
from src.infrastructure.database.database_adapter import DatabaseAdapter
from src.infrastructure.cache.redis_adapter import RedisAdapter
from src.infrastructure.config import settings


async def main():
    print("--- Iniciando Teste de Integração dos Adaptadores ---\n")

    account_id_teste = "conta-12345"
    saldo_inicial = 1500.50

    # 1. Testando o PostgreSQL
    print("1. Testando PostgresAccountAdapter...")
    pg_adapter = DatabaseAdapter()

    # Gravando no banco
    print(f"   -> Atualizando saldo da {account_id_teste} para R$ {saldo_inicial}")
    await pg_adapter.update_balance(account_id_teste, saldo_inicial)

    # Lendo do banco
    saldo_db = await pg_adapter.get_balance(account_id_teste)
    print(f"   -> Saldo lido do PostgreSQL: R$ {saldo_db}")
    assert saldo_db == saldo_inicial, "Erro: Saldo do banco não bate!"

    print("\n2. Testando RedisCacheAdapter...")
    redis_adapter = RedisAdapter(settings.REDIS_URL)

    # Gravando no Cache
    print(f"   -> Salvando saldo no cache Redis por 60 segundos...")
    await redis_adapter.set(f"balance:{account_id_teste}", str(saldo_db), ttl_seconds=60)

    # Lendo do Cache
    saldo_cache = await redis_adapter.get(f"balance:{account_id_teste}")
    print(f"   -> Saldo lido do Redis: R$ {saldo_cache}")
    assert float(saldo_cache) == saldo_inicial, "Erro: Saldo do cache não bate!"

    # Fechando conexão do Redis
    await redis_adapter.close()

    print("\n--- ✅ Todos os adaptadores funcionaram perfeitamente! ---")


if __name__ == "__main__":
    asyncio.run(main())