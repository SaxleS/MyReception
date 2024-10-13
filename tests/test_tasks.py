from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect
import websockets
import json


@pytest.fixture
def example_task():
    # Фикстура для создания примера задачи
    return {
        "country": "USA",
        "city": "New York",
        "start_coordinates": {
            "latitude": 40.712776,
            "longitude": -74.005974
        },
        "checkpoints": [
            {
                "latitude": 40.712776,
                "longitude": -74.005974
            },
            {
                "latitude": 40.730610,
                "longitude": -73.935242
            }
        ],
        "description": "Доставить груз из центрального парка к зданию на пятой авеню"
    }

@pytest.fixture
def create_test_user(client):
    # Регистрация и подтверждение пользователя перед тестами
    register_data = {
        "username": "testuser",
        "email": "nousyn@icloud.com",
        "password": "testpassword"
    }
    register_response = client.post("/api/v1/register", json=register_data)
    assert register_response.status_code == 200

    # Подтверждение email с кодом активации
    activation_code = "1234"
    confirm_response = client.post("/api/v1/confirm-email", json={
        "username": "testuser",
        "activation_code": activation_code
    })
    assert confirm_response.status_code == 200

@pytest.fixture
def auth_headers(client, create_test_user):
    # Логин и получение токена для тестов
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/api/v1/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Тест создания новой задачи
def test_create_task(client, example_task, auth_headers):
    response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Task created successfully"
    assert "task_id" in data

# Тест получения всех задач
def test_get_all_tasks(client, auth_headers):
    response = client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Должен вернуться список задач

# Тест получения задачи по ID
def test_get_task_by_id(client, example_task, auth_headers):
    # Сначала создаем задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert create_response.status_code == 200  # Убедимся, что задача создана успешно
    task_id = create_response.json()["task_id"]

    # Теперь пытаемся получить её по ID
    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200  # Убедимся, что запрос успешен
    data = response.json()

    # Проверяем значения полей задачи
    assert data["city"] == "New York"
    assert data["country"] == "USA"
    
    # Проверяем, что ключевые точки (checkpoints) возвращаются в виде списка
    assert "checkpoints" in data
    assert isinstance(data["checkpoints"], list)

    # Проверяем, что поле stream_url присутствует и может быть None (если не начата трансляция)
    assert "stream_url" in data
    assert data["stream_url"] is None or isinstance(data["stream_url"], str)

# Тест удаления задачи
def test_delete_task(client, example_task, auth_headers):
    # Сначала создаем задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    task_id = create_response.json()["task_id"]

    # Теперь удаляем её
    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task deleted successfully"

    # Проверяем, что задача была удалена
    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"





# Тест принятия задачи
def test_accept_task(client, example_task, auth_headers):
    # Создаём задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]

    # Принимаем задачу
    accept_response = client.post(f"/api/v1/tasks/{task_id}/accept", headers=auth_headers)
    assert accept_response.status_code == 200
    data = accept_response.json()
    
    # Проверяем, что задача принята
    assert data["message"] == "Task accepted successfully"
    assert "stream_url" in data
    assert isinstance(data["stream_url"], str)



    # Тест завершения задачи
def test_complete_task(client, example_task, auth_headers):
    # Создаём задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]

    # Принимаем задачу
    accept_response = client.post(f"/api/v1/tasks/{task_id}/accept", headers=auth_headers)
    assert accept_response.status_code == 200

    # Завершаем задачу
    complete_response = client.post(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["message"] == "Task completed successfully"


    # Тест просмотра видеопотока задачи
def test_watch_task(client, example_task, auth_headers):
    # Сначала создаем задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]

    # Принимаем задачу
    accept_response = client.post(f"/api/v1/tasks/{task_id}/accept", headers=auth_headers)
    assert accept_response.status_code == 200

    # Теперь пытаемся получить ссылку на видеопоток
    watch_response = client.get(f"/api/v1/tasks/{task_id}/watch", headers=auth_headers)
    assert watch_response.status_code == 200
    data = watch_response.json()

    # Проверяем, что URL видеопотока возвращается корректно
    assert "stream_url" in data
    assert isinstance(data["stream_url"], str)


# # Тест для подключения к WebSocket видеопотока

# @pytest.mark.asyncio
# async def test_video_stream(client, example_task, auth_headers):
#     # Создаём задачу
#     create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
#     assert create_response.status_code == 200
#     task_id = create_response.json()["task_id"]

#     # Исполнитель принимает задачу
#     accept_response = client.post(f"/api/v1/tasks/{task_id}/accept", headers=auth_headers)
#     assert accept_response.status_code == 200
#     stream_url = accept_response.json()["stream_url"]

#     # Логирование URL для подключения
#     print(f"Connecting to WebSocket URL: {stream_url}")

#     # Подключение стримера
#     async with websockets.connect(f"{stream_url}/streamer") as streamer_socket:
#         # Подключение зрителя
#         async with websockets.connect(f"{stream_url}/viewer") as viewer_socket:
#             # Стример отправляет offer
#             offer = {"type": "offer", "sdp": "sample_sdp_data"}
#             await streamer_socket.send(json.dumps(offer))

#             # Зритель ждет ответ
#             data = await viewer_socket.recv()
#             print(f"Viewer received: {data}")
#             assert "sdp" in json.loads(data)


@pytest.mark.asyncio
async def test_websocket_streamer_viewer(client: TestClient, example_task, auth_headers):
    # Создаём задачу
    create_response = client.post("/api/v1/create-task", json=example_task, headers=auth_headers)
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]

    # Исполнитель принимает задачу
    accept_response = client.post(f"/api/v1/tasks/{task_id}/accept", headers=auth_headers)
    assert accept_response.status_code == 200
    stream_url = accept_response.json()["stream_url"]

    # Логирование URL для подключения
    print(f"Connecting to WebSocket URL for streamer and viewer: {stream_url}")

    # Подключение стримера
    async with websockets.connect(f"ws://127.0.0.1:8002/ws/video/{task_id}/streamer") as streamer_socket:
        # Подключение зрителя
        async with websockets.connect(f"ws://127.0.0.1:8002/ws/video/{task_id}/viewer") as viewer_socket:
            # Стример отправляет SDP offer
            offer = {"type": "offer", "sdp": "sample_sdp_data"}
            await streamer_socket.send(json.dumps(offer))

            # Зритель получает SDP offer
            viewer_data = await viewer_socket.recv()
            viewer_message = json.loads(viewer_data)
            print(f"Viewer received: {viewer_message}")

            # Проверка полученного SDP offer зрителем
            assert viewer_message["type"] == "offer"  # Зритель должен получить offer

            # Зритель отправляет SDP answer
            answer = {"type": "answer", "sdp": "sample_sdp_answer"}
            await viewer_socket.send(json.dumps(answer))

            # Стример получает SDP answer
            streamer_data = await streamer_socket.recv()
            streamer_message = json.loads(streamer_data)
            print(f"Streamer received: {streamer_message}")

            # Проверка полученного SDP ответа стримера
            assert streamer_message["type"] == "answer"  # Стример должен получить answer