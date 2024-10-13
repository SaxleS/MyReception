from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from teleport_webrtc.core.database import get_db
from teleport_webrtc.schemas.tasks import CreatorOut, TaskCreate, TaskOut
from teleport_webrtc.crud.tasks import TaskCRUD
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
import os
from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearer
import json
import websockets
from sqlalchemy.ext.asyncio import AsyncSession



# Загружаем переменные из файла .env
load_dotenv()

# Читаем секретный ключ из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

# Инициализация JWT
jwt_bearer = JwtAccessBearer(secret_key=SECRET_KEY)



# Объект для управления соединениями WebSocket
class ConnectionManager:
    def __init__(self):
        self.streamers = {}
        self.viewers = {}

    async def connect_streamer(self, task_id: int, websocket: WebSocket):
        await websocket.accept()
        self.streamers[task_id] = websocket

    async def connect_viewer(self, task_id: int, websocket: WebSocket):
        await websocket.accept()
        self.viewers[task_id] = websocket

    def disconnect_streamer(self, task_id: int):
        if task_id in self.streamers:
            del self.streamers[task_id]

    def disconnect_viewer(self, task_id: int):
        if task_id in self.viewers:
            del self.viewers[task_id]

    async def send_sdp(self, task_id: int, message: dict):
        if task_id in self.viewers:
            await self.viewers[task_id].send_text(json.dumps(message))

manager = ConnectionManager()









async def send_sdp_offer(stream_url, sdp_offer):
    async with websockets.connect(stream_url) as websocket:
        await websocket.send(json.dumps({
            "type": "offer",
            "sdp": sdp_offer
        }))
        response = await websocket.recv()
        return json.loads(response)




@router.post("/create-task", response_model=dict)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)  # JWT токен
):
    user_id = credentials.subject['id']  # Извлекаем ID пользователя из JWT токена
    task_crud = TaskCRUD(db)
    new_task = await task_crud.create_task(task, user_id=user_id)  # Передаем ID пользователя
    return {"message": "Task created successfully", "task_id": new_task.id}


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)  # Проверка JWT
):
    task_crud = TaskCRUD(db)
    
    # Добавляем await перед вызовом асинхронного метода
    task = await task_crud.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Возвращаем задачу с информацией о создателе
    return TaskOut(
        id=task.id,
        country=task.country,
        city=task.city,
        start_coordinates={"latitude": task.start_latitude, "longitude": task.start_longitude},
        checkpoints=[{"latitude": cp['latitude'], "longitude": cp['longitude']} for cp in task.checkpoints],
        description=task.description,
        stream_url=task.stream_url,  # Передаём stream_url, даже если он None
        creator=CreatorOut(
            id=task.creator.id,
            username=task.creator.username,
            email=task.creator.email
        )
    )

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),  # Используем AsyncSession для асинхронной работы с БД
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)  # Проверка JWT
):
    task_crud = TaskCRUD(db)
    
    # Необходимо использовать await для асинхронного вызова метода
    deleted = await task_crud.delete_task(task_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

@router.get("/tasks", response_model=List[TaskOut])
async def get_all_tasks(
    db: AsyncSession = Depends(get_db),
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)  # Проверка JWT
):
    task_crud = TaskCRUD(db)
    tasks = await task_crud.get_all_tasks()

    tasks_out = []
    for task in tasks:
        # Создаем объект TaskOut вручную, передавая start_coordinates как вложенный объект
        task_out = TaskOut(
            id=task.id,
            country=task.country,
            city=task.city,
            start_coordinates={
                "latitude": task.start_latitude,
                "longitude": task.start_longitude
            },
            checkpoints=[{"latitude": cp['latitude'], "longitude": cp['longitude']} for cp in task.checkpoints],
            description=task.description,
            stream_url=task.stream_url,
            creator=task.creator  # Автоматически будет преобразован через from_orm
        )
        tasks_out.append(task_out)

    return tasks_out







@router.post("/tasks/{task_id}/accept", response_model=dict)
async def accept_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),  # Изменено на AsyncSession
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
):
    task_crud = TaskCRUD(db)
    
    # Ждем результат выполнения асинхронного метода
    task = await task_crud.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.executor_id:
        raise HTTPException(status_code=400, detail="Task already accepted")

    # Принятие задачи исполнителем (await перед асинхронной функцией)
    await task_crud.accept_task(task_id, executor_id=credentials.subject["id"])
    
    # Обновление задачи после принятия
    task = await task_crud.get_task_by_id(task_id)
    
    return {"message": "Task accepted successfully", "stream_url": task.stream_url}



# Завершить задачу
@router.post("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),  # Изменено на AsyncSession
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
):
    task_crud = TaskCRUD(db)
    
    # Ждем результат выполнения асинхронного метода
    task = await task_crud.get_task_by_id(task_id)
    
    if not task or task.executor_id != credentials.subject["id"]:
        raise HTTPException(status_code=403, detail="You are not the executor of this task")
    
    # Завершаем задачу (await перед асинхронной функцией)
    await task_crud.complete_task(task_id)
    
    return {"message": "Task completed successfully"}


@router.get("/tasks/{task_id}/watch")
async def watch_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),  # Изменил на AsyncSession
    credentials: JwtAuthorizationCredentials = Depends(jwt_bearer)
):
    task_crud = TaskCRUD(db)
    
    # Используем await для асинхронного метода
    task = await task_crud.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.stream_url:
        raise HTTPException(status_code=400, detail="Stream not started yet")
    
    # Возвращаем URL потока для просмотра
    return {"stream_url": task.stream_url}



# Маршрут для подключения стримера (WebSocket)
@router.websocket("/ws/video/{task_id}/streamer")
async def streamer_websocket(websocket: WebSocket, task_id: int):
    await manager.connect_streamer(task_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'offer':
                # Стример отправляет SDP offer, пересылаем зрителю
                await manager.send_sdp(task_id, message)
    except WebSocketDisconnect:
        manager.disconnect_streamer(task_id)
        print(f"Streamer for task {task_id} disconnected")

# Маршрут для подключения зрителя (WebSocket)
@router.websocket("/ws/video/{task_id}/viewer")
async def viewer_websocket(websocket: WebSocket, task_id: int):
    await manager.connect_viewer(task_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Зритель ожидает offer от стримера и может принять SDP answer
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect_viewer(task_id)
        print(f"Viewer for task {task_id} disconnected")

