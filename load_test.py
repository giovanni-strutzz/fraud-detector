import asyncio
import os

import aiohttp
import random
import time
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = f"http://localhost:{os.getenv('APP_PORT', '8000')}/transfers/transfer"

NUM_ACCOUNTS = 50
ACCOUNT_IDS = [f"conta-loadtest-{i}" for i in range(1, NUM_ACCOUNTS + 1)]


async def seed_database():
    print(f"🌱 [Fase 1] Criando/Atualizando {NUM_ACCOUNTS} contas de teste no banco...")
    engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True, pool_recycle=3600)

    async with engine.begin() as conn:
        for account_id in ACCOUNT_IDS:
            query = text("""
                         INSERT INTO accounts (account_id, balance, transaction_behavior_embedding)
                         VALUES (:account_id, :balance, CAST(:embedding AS vector)) ON CONFLICT (account_id) DO
                         UPDATE
                             SET balance = EXCLUDED.balance,
                             transaction_behavior_embedding = EXCLUDED.transaction_behavior_embedding;
                         """)

            await conn.execute(query, {
                "account_id": account_id,
                "balance": 10000.00,
                "embedding": "[0.05, 0.5, 0.2]"
            })

    await engine.dispose()
    print("✅ [Fase 1] Concluída! Todas as contas estão prontas com R$ 10.000,00 e vetores salvos.\n")


def get_random_accounts():
    origin = random.choice(ACCOUNT_IDS)
    destination = random.choice(ACCOUNT_IDS)
    while destination == origin:
        destination = random.choice(ACCOUNT_IDS)
    return origin, destination


def generate_normal_payload():
    origin, destination = get_random_accounts()
    return {
        "origin_account_id": origin,
        "destination_account_id": destination,
        "origin_document": "11122233344",
        "destination_document": "99988877766",
        "amount": round(random.uniform(50.0, 300.0), 2),
        "origin_bank_code": "001",
        "destination_bank_code": "033"
    }


def generate_fraud_payload():
    origin, destination = get_random_accounts()
    return {
        "origin_account_id": origin,
        "destination_account_id": destination,
        "origin_document": "11122233344",
        "destination_document": "99988877766",
        "amount": round(random.uniform(5000.0, 9500.0), 2),
        "origin_bank_code": "001",
        "destination_bank_code": "999"
    }


async def send_request(session, request_id):
    is_fraud = random.random() < 0.2
    payload = generate_fraud_payload() if is_fraud else generate_normal_payload()

    headers = {'Content-Type': 'application/json'}
    start_time = time.time()

    try:
        async with session.post(API_URL, json=payload, headers=headers) as response:
            status = response.status
            data = await response.json()
            elapsed = time.time() - start_time

            tipo = "🚨 FRAUDE" if is_fraud else "✅ NORMAL"
            if status == 202:
                print(f"[{request_id}] {tipo} | 📨 Kafka OK ({elapsed:.3f}s) | Origem: {payload['origin_account_id']}")
            elif status == 400:
                # Pode ser bloqueio por Fraude ou Saldo Insuficiente
                print(f"[{request_id}] {tipo} | 🛡️ Bloqueado: {data.get('detail')} ({elapsed:.3f}s)")
            else:
                print(f"[{request_id}] {tipo} | ❌ Erro {status}: {data}")
    except Exception as e:
        print(f"[{request_id}] Falha na requisição HTTP: {e}")


async def main():
    await seed_database()

    TOTAL_REQUESTS = 500
    print(f"🚀 [Fase 2] Iniciando bombardeio de {TOTAL_REQUESTS} transações concorrentes...")

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(TOTAL_REQUESTS)]
        await asyncio.gather(*tasks)

    print("\n🏁 Simulação de estresse concluída com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())