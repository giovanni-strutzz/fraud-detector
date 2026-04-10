import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()


async def verify_redis_cache():
    print("🔍 Verificando persistência no Redis...")

    # Conecta ao Redis
    r = redis.from_url(os.getenv("REDIS_URL"))

    # Vamos verificar as contas que o load_test criou (ex: as primeiras 5)
    test_accounts = [f"balance:conta-loadtest-{i}" for i in range(1, 6)]

    found_count = 0
    for key in test_accounts:
        value = await r.get(key)
        if value:
            print(f"✅ Key encontrada: {key} | Saldo no Cache: R$ {value.decode('utf-8')}")
            found_count += 1
        else:
            print(f"❌ Key NÃO encontrada: {key}")

    if found_count > 0:
        print(f"\n🚀 Sucesso! O Worker está populando o Redis corretamente.")
    else:
        print(f"\n⚠️ Alerta: Nenhuma chave encontrada. Verifique se o Worker está rodando.")

    await r.close()


if __name__ == "__main__":
    asyncio.run(verify_redis_cache())