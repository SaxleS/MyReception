import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_register_user(async_client):
    """
    Тест успешной регистрации пользователя.
    """
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
    }

    response = await async_client.post("/api/v1/register", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Registration successful"


@pytest.mark.asyncio
async def test_resend_verification_code(async_client):
    """
    Тест повторной отправки кода верификации.
    """
    email = "testuser@example.com"
    request_data = {"email": email}

    with patch("app.celery.celery_tasks.send_email_task", new=AsyncMock()) as mock_send_email:
        response = await async_client.post("/api/v1/resend-verification-code", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Verification code sent"
    mock_send_email.delay.assert_called_once_with(
        recipient=email,
        subject="MyReception - Activation Code",
        body="Ваш код активации: 1234",
    )