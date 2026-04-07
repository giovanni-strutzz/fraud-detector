from dataclasses import dataclass
from src.ports.output.repository.AccountRepository import AccountRepository, CacheRepository


@dataclass(frozen=True)
class GetBalanceQuery:
    account_id: str


class GetBalanceUseCase:
    def __init__(self, account_repository: AccountRepository, cache_repository: CacheRepository):
        self.repository = account_repository
        self.cache = cache_repository

    async def execute(self, query: GetBalanceQuery) -> dict:
        cache_key = f"balance: {query.account_id}"
        cached_balance = await self.cache.get(cache_key)

        if cached_balance is not None:
            return {
                "account_id": query.account_id,
                "balance": float(cached_balance),
                "source": "redis-cache"
            }

        db_balance = await self.repository.get_balance(query.account_id)

        if db_balance is None:
            raise ValueError(f"Account: {query.account_id} not found")

        await self.cache.set(cache_key, str(db_balance), ttl_seconds=3600)

        return {
            "account_id": query.account_id,
            "balance": db_balance,
            "source": "postgres-db"
        }