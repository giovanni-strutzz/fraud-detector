import logging
from uuid import uuid4
from src.application.command.RequestTransferCommand import RequestTransferCommand
from src.ports.output.EventUseCase import PublisherEvent
from src.domain.events.events import RequestedTransfer
from src.ports.output.repository.AccountRepository import AccountRepository


logger = logging.getLogger(__name__)

class RequestTransfer:
    def __init__(self, publisher: PublisherEvent, topic: str, db_repository: AccountRepository):
        self.publisher = publisher
        self.topic = topic
        self.db_repository = db_repository


    async def execute(self, command: RequestTransferCommand) -> dict:
        current_balance = await self.db_repository.get_balance(command.origin_account_id)

        if current_balance is None:
            raise ValueError(f"Origin Account {command.origin_account_id} not found!")

        if current_balance < command.amount:
            raise ValueError("Insufficient funds for transfer!")

        normalized_account = min(command.amount / 10000.0, 1.0)
        destination_bank_risk = 0.8 if command.destination_bank_code == '999' else 0.2
        simulated_frequency = 0.5
        current_embedding = [normalized_account, simulated_frequency, destination_bank_risk]

        distance = await self.db_repository.calculate_behavior_distance(
            command.origin_account_id,
            current_embedding
        )

        print(f"Fraud Detector | Account: {command.origin_account_id} | Vectorial Distance: {distance:.4f}")

        if distance is not None and distance > 0.4:
            raise ValueError("FRAUD DETECTED: Suspect Transactional Behavior. Blocked transaction!")

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
            "status": "Processing Asynchronously...",
        }
