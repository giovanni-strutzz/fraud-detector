from abc import ABC, abstractmethod
from typing import Optional


class AccountRepository(ABC):

    @abstractmethod
    async def get_balance(self, account_id: str) -> Optional[float]:
        pass

    @abstractmethod
    async def update_balance(self, account_id: str, amount: float) -> None:
        pass

    @abstractmethod
    async def update_embedding(self, account_id: str, embedding: list[float]) -> None:
        pass


class CacheRepository(ABC):

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        pass