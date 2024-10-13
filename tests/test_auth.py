def test_register_user(client):
    # Тест регистрации нового пользователя
    response = client.post("/api/v1/register", json={
        "username": "testuser",
        "email": "nousyn@icloud.com",  # Используем указанный email
        "password": "testpassword"
    })
    assert response.status_code == 200
    
    # Временно выведем JSON-ответ для отладки
    print(response.json())  # Для проверки, что фактически возвращается
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "message" in data  # Проверяем наличие ключа 'message'
    assert data["message"] == "Registration successful. Please check your email for the activation code."

def test_confirm_email(client):
    # Тест подтверждения email с кодом активации
    register_response = client.post("/api/v1/register", json={
        "username": "testuser",
        "email": "nousyn@icloud.com",  # Используем указанный email
        "password": "testpassword"
    })
    assert register_response.status_code == 200

    # Имитируем код активации (его можно замокировать в реальном тестировании)
    activation_code = "1234"  # Подставьте реальный код, если есть доступ к базе или мок системе

    # Подтверждаем email
    response = client.post("/api/v1/confirm-email", json={
        "username": "testuser",
        "activation_code": activation_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Email confirmed successfully!"

def test_login_user(client):
    # Тест логина пользователя после подтверждения email
    client.post("/api/v1/register", json={
        "username": "testuser",
        "email": "nousyn@icloud.com",
        "password": "testpassword"
    })
    
    # Имитируем подтверждение email
    activation_code = "1234"
    client.post("/api/v1/confirm-email", json={
        "username": "testuser",
        "activation_code": activation_code
    })

    # Логинимся после подтверждения email
    response = client.post("/api/v1/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_access_protected_route(client):
    # Тест доступа к защищённому маршруту с использованием access token
    register_response = client.post("/api/v1/register", json={
        "username": "testuser",
        "email": "nousyn@icloud.com",
        "password": "testpassword"
    })
    tokens = register_response.json()

    # Имитируем подтверждение email
    activation_code = "1234"
    client.post("/api/v1/confirm-email", json={
        "username": "testuser",
        "activation_code": activation_code
    })

    # Доступ к защищённому маршруту
    response = client.get("/api/v1/protected", headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Hello testuser!"

def test_access_protected_route_without_token(client):
    # Тест доступа к защищённому маршруту без токена
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Credentials are not provided"