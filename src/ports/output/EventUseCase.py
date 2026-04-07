from abc import ABC, abstractmethod
from src.domain.events.events import DomainEvent
from src.domain.entities.entities import Account


class PublisherEvent(ABC):

    @abstractmethod
    async def publish(self, topic: str, event: DomainEvent) -> None:
        pass


class AccountRepository(ABC):

    @abstractmethod
    async def get_by_id(self, account_id: str) -> Account:
        pass