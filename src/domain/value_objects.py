from dataclasses import dataclass
from decimal import Decimal
import re


@dataclass(frozen=True)
class CPF:
    value: str

    def __post_init__(self):
        if not re.match(r"^\d{11}$", self.value):
            raise ValueError(f"CPF {self.value} is not a valid CPF")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError(f"Value must be greater than 0")