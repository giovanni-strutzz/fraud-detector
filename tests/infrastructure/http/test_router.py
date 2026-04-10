from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.main import app
from src.infrastructure.http.routers import get_use_case

client = TestClient(app)


def test_post_transfer_success():
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = {"status": "Accepted", "transaction_id": "123"}

    app.dependency_overrides[get_use_case] = lambda: mock_use_case

    payload = {
        "origin_account_id": "conta-1",
        "destination_account_id": "conta-2",
        "origin_document": "11122233344",
        "destination_document": "99988877766",
        "amount": 150.0,
        "origin_bank_code": "001",
        "destination_bank_code": "033"
    }

    response = client.post("/transfers/transfer", json=payload)

    assert response.status_code == 202
    assert response.json()["status"] == "Accepted"

    app.dependency_overrides.clear()