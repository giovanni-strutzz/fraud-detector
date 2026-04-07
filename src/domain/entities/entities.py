from dataclasses import dataclass, field
from uuid import UUID
from typing import List
from src.domain.value_objects import Money
from src.domain.events.events import DomainEvent


@dataclass
class Account:
    account_id: str
    balance: Money
    owner_document: str
    _changes: List[DomainEvent] = field(default_factory=list)

    def withdraw(self, value: Money):
        if self.balance.amount < value.amount:
            raise ValueError(f"Insufficient funds to withdraw {value}")
            