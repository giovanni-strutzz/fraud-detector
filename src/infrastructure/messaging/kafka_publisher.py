import json
import logging
from confluent_kafka import Producer
from src.ports.output.EventUseCase import PublisherEvent
from src.domain.events.events import DomainEvent


logger = logging.getLogger(__name__)


class KafkaPublisher(PublisherEvent):
    def __init__(self, bootstrap_servers: str):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'fintech-core-service',
            'acks': 'all',
        }

        self.producer = Producer(self.conf)

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Failed to deliver event: {err}")
        else:
            logger.info(f"Successfully deliver event: {msg} on topic: {msg.topic()}. [Partition: {msg.partition()}]")


    async def publish(self, topic: str, event: DomainEvent) -> None:
        try:
            event_dict = event.model_dump(mode='json')
            event_json = json.dumps(event_dict)

            partition_key = str(event_dict.get('transaction_id', event.event_id))

            self.producer.produce(
                topic=topic,
                key=partition_key.encode('utf-8'),
                value=event_json.encode('utf-8'),
                callback=self._delivery_report
            )

            self.producer.poll(0)
        except Exception as exc:
            logger.error(f"Failed to publish event: {exc}")
            raise