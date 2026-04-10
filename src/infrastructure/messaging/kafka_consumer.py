import json
import logging
import asyncio
from confluent_kafka import Consumer, KafkaError
from src.infrastructure.config import settings
from src.infrastructure.database.database_adapter import DatabaseAdapter
from src.infrastructure.cache.redis_adapter import RedisAdapter

logger = logging.getLogger(__name__)


class TransformerConsumer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'projection-group',
            'auto.offset.reset': 'earliest',
        }

        self.consumer = Consumer(self.conf)
        self.adapter = DatabaseAdapter()
        self.redis_adapter = RedisAdapter(settings.REDIS_URL)

    async def process_message(self, message):
        try:
            data = json.loads(message.value().decode('utf-8'))
            account_id = data['origin_account_id']
            transfered_amount = data['value']

            print(f"Processing message: {account_id} | Value: {transfered_amount}")

            current_balance = await self.adapter.get_balance(account_id) or 0.0
            new_balance = current_balance - transfered_amount

            await self.adapter.update_balance(account_id, new_balance)

            await self.redis_adapter.set(
                f"balance:{account_id}",
                str(new_balance),
                ttl_seconds=3600
            )

            normalized_value = min(transfered_amount / 10000.0, 1.0)
            destination_bank_risk = 0.8 if data['destination_bank_code'] == '999' else 0.2
            simulated_frequency = 0.5

            behaviorial_vector = [normalized_value, simulated_frequency, destination_bank_risk]

            await self.adapter.update_embedding(account_id, behaviorial_vector)

            print(f"Processed message: {account_id} | New Balance: {new_balance}")

        except Exception as exc:
            logger.error(f"Error to process message: Exception: {exc}")



    def run(self):
        self.consumer.subscribe([settings.KAFKA_TOPIC_TRANSFERS])

        print(f"Started Worker. Listener topics: {settings.KAFKA_TOPIC_TRANSFERS}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(msg.error())
                    break

                loop.run_until_complete(self.process_message(msg))
        finally:
            self.consumer.close()
            loop.close()
