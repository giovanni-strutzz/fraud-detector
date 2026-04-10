import logging

from typing import Optional
from sqlalchemy import select, text
from src.ports.output.repository.AccountRepository import AccountRepository
from src.infrastructure.database.base import AsyncSessionLocal, AccountModel

logger = logging.getLogger(__name__)


class DatabaseAdapter(AccountRepository):
    async def get_balance(self, account_id: str) -> Optional[float]:
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(AccountModel.balance).where(AccountModel.account_id == account_id)
                result = await session.execute(stmt)
                balance = result.scalar_one_or_none()

                return balance
            except Exception as exc:
                logger.error(f"Error getting balance for {account_id}")

    async def update_balance(self, account_id: str, new_balance: float) -> None:
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(AccountModel).where(AccountModel.account_id == account_id)
                result = await session.execute(stmt)
                account = result.scalar_one_or_none()

                if account:
                    account.balance = new_balance
                else:
                    account = AccountModel(
                        account_id=account_id,
                        balance=new_balance,
                        document="00000000000",
                        transaction_behavior_embedding=[0.0, 0.0, 0.0]
                    )

                    session.add(account)

                await session.commit()
            except Exception as exc:
                await session.rollback()
                logger.error(f"Error updating balance for {account_id}: Error: {exc}")
                raise

    async def update_embedding(self, account_id: str, embedding: list[float]) -> None:
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(AccountModel).where(AccountModel.account_id == account_id)
                result = await session.execute(stmt)
                account = result.scalar_one_or_none()

                if account:
                    account.transaction_behavior_embedding = embedding
                    await session.commit()
            except Exception as exc:
                logger.error(f"Error updating embedding for {account_id}: Error: {exc}")
                raise


    async def calculate_behavior_distance(self, account_id: str, transaction_embedding: list[float]) -> float | None:
        async with AsyncSessionLocal() as session:
            try:
                embedding_str = f"[{','.join(map(str, transaction_embedding))}]"

                query = text("""
                    SELECT transaction_behavior_embedding <-> CAST(:embedding AS vector) AS distance
                    FROM accounts
                    WHERE account_id = :account_id
                """)

                result = await session.execute(query, {"embedding": embedding_str, "account_id": account_id})
                row = result.fetchone()

                if row and row[0] is not None:
                    return float(row[0])

                return None
            except Exception as exc:
                logger.error(f"Error calculating behavior distance for {account_id}: Error: {exc}")
                return None
