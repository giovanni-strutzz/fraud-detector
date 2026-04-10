import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from src.infrastructure.messaging.kafka_consumer import TransformerConsumer


@pytest.mark.asyncio
@patch("src.infrastructure.messaging.kafka_consumer.Consumer")
@patch("src.infrastructure.messaging.kafka_consumer.DatabaseAdapter")
@patch("src.infrastructure.messaging.kafka_consumer.RedisAdapter")
async def test_transformer_consumer_process_message(mock_redis_class, mock_db_class, mock_consumer_class):
    mock_db_instance = mock_db_class.return_value
    mock_db_instance.get_balance = AsyncMock(return_value=1000.0)
    mock_db_instance.update_balance = AsyncMock()
    mock_db_instance.update_embedding = AsyncMock()

    mock_redis_instance = mock_redis_class.return_value
    mock_redis_instance.set = AsyncMock()

    consumer = TransformerConsumer()

    payload = {
        "origin_account_id": "conta-123",
        "value": 200.0,
        "destination_bank_code": "999"
    }

    mock_message = MagicMock()
    mock_message.value.return_value = json.dumps(payload).encode('utf-8')

    await consumer.process_message(mock_message)

    mock_db_instance.get_balance.assert_called_once_with("conta-123")

    mock_db_instance.update_balance.assert_called_once_with("conta-123", 800.0)

    mock_redis_instance.set.assert_called_once_with(
        "balance:conta-123",
        "800.0",
        ttl_seconds=3600
    )

    mock_db_instance.update_embedding.assert_called_once()

    args, kwargs = mock_db_instance.update_embedding.call_args
    assert args[0] == "conta-123"
    vector = args[1]

    assert vector[0] == 0.02
    assert vector[2] == 0.8