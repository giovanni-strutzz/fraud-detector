from pydantic import BaseModel, Field


class RequestTransferHttp(BaseModel):
    origin_account_id: str = Field(..., description="Origin account ID")
    destination_account_id: str = Field(..., description="Destination account ID")
    origin_document: str = Field(..., description="Origin Document Number")
    destination_document: str = Field(..., description="Destination Document Number")
    amount: float = Field(..., gt=0, description="Amount of transfer")
    origin_bank_code: str
    destination_bank_code: str