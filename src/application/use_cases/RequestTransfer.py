from uuid import uuid4
from src.application.command.RequestTransferCommand import RequestTransferCommand
from src.ports.output.EventUseCase import PublisherEvent
from src.domain.events.events import RequestedTransfer


class RequestTransfer:
    def __init__(self, publisher: PublisherEvent, topic: str):
        self.publisher = publisher
        self.topic = topic


    async def execute(self, command: RequestTransferCommand) -> dict:
        transaction_id = uuid4()

        event = RequestedTransfer(
            event_id=uuid4(),
            transaction_id=transaction_id,
            origin_account_id=command.origin_account_id,
            destination_account_id=command.destination_account_id,
            origin_document=command.origin_document,
            destination_document=command.destination_document,
            value=command.amount,
            origin_bank_code=command.origin_bank_code,
            destination_bank_code=command.destination_bank_code
        )

        await self.publisher.publish(event=event, topic=self.topic)

        return {
            "transaction_id": str(transaction_id),
            "status": "Processing asynchronously...",
        }