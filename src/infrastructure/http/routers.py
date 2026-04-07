from fastapi import APIRouter, Depends, status, HTTPException

from src.application.query.get_balance import GetBalanceUseCase, GetBalanceQuery
from src.infrastructure.cache.redis_adapter import RedisAdapter
from src.infrastructure.database.database_adapter import DatabaseAdapter
from src.infrastructure.http.schemas import RequestTransferHttp
from src.application.command.RequestTransferCommand import RequestTransferCommand
from src.application.use_cases.RequestTransfer import RequestTransfer
from src.infrastructure.messaging.kafka_publisher import KafkaPublisher
from src.infrastructure.config import settings

router = APIRouter(prefix="/transfers", tags=["Transfers"])

_global_kafka_publisher = KafkaPublisher(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

def get_use_case():
    database_adapter = DatabaseAdapter()

    return RequestTransfer(
        publisher=_global_kafka_publisher,
        topic=settings.KAFKA_TOPIC_TRANSFERS,
        db_repository=database_adapter
    )

def get_balance_use_case():
    db = DatabaseAdapter()
    cache = RedisAdapter(settings.REDIS_URL)

    return GetBalanceUseCase(account_repository=db,cache_repository=cache)


@router.get("/accounts/{account_id}/balance", tags=["Accounts"])
async def get_balance(account_id: str, use_case: GetBalanceUseCase = Depends(get_balance_use_case)):
    try:
        query = GetBalanceQuery(account_id=account_id)
        result = await use_case.execute(query)

        return result
    except ValueError as vex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(vex))


@router.post("/transfer", status_code=status.HTTP_202_ACCEPTED)
async def request_transfer(
        payload: RequestTransferHttp,
        use_case: RequestTransfer = Depends(get_use_case)
):
    command = RequestTransferCommand(
        origin_account_id=payload.origin_account_id,
        destination_account_id=payload.destination_account_id,
        origin_document=payload.origin_document,
        destination_document=payload.destination_document,
        amount=payload.amount,
        origin_bank_code=str(payload.origin_bank_code),
        destination_bank_code=str(payload.destination_bank_code)
    )

    try:
        result = await use_case.execute(command)

        return result
    except ValueError as vex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(vex))