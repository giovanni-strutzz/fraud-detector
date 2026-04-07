from dataclasses import dataclass


@dataclass(frozen=True)
class RequestTransferCommand:
    origin_account_id: str
    destination_account_id: str
    origin_document: str
    destination_document: str
    amount: float
    origin_bank_code: str
    destination_bank_code: str
