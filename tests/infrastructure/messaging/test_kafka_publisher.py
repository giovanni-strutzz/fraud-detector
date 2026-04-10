import pytest
import json
from unittest.mock import MagicMock
from src.infrastructure.messaging.kafka_publisher import KafkaPublisher
from src.domain.events.events import DomainEvent


@pytest.mark.asyncio
async def test_kafka_publisher_success():
    publisher = KafkaPublisher(bootstrap_servers="fake:9092")

    mock_producer_instance = MagicMock()
    publisher.producer = mock_producer_instance

    mock_event = MagicMock(spec=DomainEvent)
    mock_event.event_id = "evt-123"

    mock_event_dict = {
        "transaction_id": "txn-999",
        "origin_account_id": "conta-1",
        "amount": 100.0
    }
    mock_event.model_dump.return_value = mock_event_dict

    topic = "requested_transfers_test"

    await publisher.publish(topic, mock_event)

    mock_producer_instance.produce.assert_called_once()

    args, kwargs = mock_producer_instance.produce.call_args

    assert kwargs["topic"] == topic
    assert kwargs["key"] == b"txn-999"
    assert kwargs["value"] == json.dumps(mock_event_dict).encode('utf-8')
    assert kwargs["callback"] == publisher._delivery_report