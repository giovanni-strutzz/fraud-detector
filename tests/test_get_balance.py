import pytest
from unittest.mock import AsyncMock
from src.application.query.get_balance import GetBalanceUseCase, GetBalanceQuery

@pytest.mark.asyncio
async def test_get_balance_cache_hit():
    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    mock_cache.get.return_value = b"1500.50"

    use_case = GetBalanceUseCase(account_repository=mock_db, cache_repository=mock_cache)

    query = GetBalanceQuery(account_id="conta-123")

    result = await use_case.execute(query)

    assert result["balance"] == 1500.50

    mock_cache.get.assert_called_once_with("balance: conta-123")
    mock_db.get_balance.assert_not_called()

@pytest.mark.asyncio
async def test_get_balance_cache_miss():
    mock_db = AsyncMock()
    mock_cache = AsyncMock()

    mock_cache.get.return_value = None
    mock_db.get_balance.return_value = 500.00

    use_case = GetBalanceUseCase(account_repository=mock_db, cache_repository=mock_cache)

    query = GetBalanceQuery(account_id="conta-999")
    result = await use_case.execute(query)

    assert result["balance"] == 500.00

    mock_cache.get.assert_called_once_with("balance: conta-999")
    mock_db.get_balance.assert_called_once_with("conta-999")
    mock_cache.set.assert_called_once_with("balance: conta-999", "500.0", ttl_seconds=3600)