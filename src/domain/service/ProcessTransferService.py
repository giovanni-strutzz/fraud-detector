from abc import ABC
from uuid import uuid4
from src.application.command.RequestTransferCommand import RequestTransferCommand
from src.ports.output.EventUseCase import PublisherEvent, AccountRepository
from src.domain.events.events import RequestedTransfer
from src.domain.value_objects import Money
from decimal import Decimal


class ProcessTransferService:
    def __init__(self, publisher: PublisherEvent, repository: AccountRepository):
        self.publisher = publisher
        self.repository = repository

    async def execute(self, command: RequestTransferCommand) -> None:

        account = await self.repository.get_by_id(command.origin_account_id)

        if not account:
            raise ValueError(f"Origin account {command.origin_account_id} not found")

        transfer_amount = Money(Decimal(str(command.amount)))

        account.withdraw(transfer_amount)

        event = RequestedTransfer(
            event_id=uuid4(),
            transaction_id=uuid4(),
            origin_account_id=command.origin_account_id,
            destination_account_id=command.destination_account_id,
            origin_document=command.origin_document,
            destination_document=command.destination_document,
            value=command.amount,
            origin_bank_code=command.origin_bank_code,
            destination_bank_code=command.destination_bank_code
        )

        await self.publisher.publish(event=event, topic="requested_transfers")