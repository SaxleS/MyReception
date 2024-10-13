from sqlalchemy.ext.asyncio import AsyncSession
from teleport_webrtc.models.tasks import Task
from teleport_webrtc.schemas.tasks import TaskCreate
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

class TaskCRUD:
    def __init__(self, db: AsyncSession):  # Используем AsyncSession
        self.db = db

    async def create_task(self, task_data: TaskCreate, user_id: int):
        serialized_checkpoints = [{
            'latitude': checkpoint.latitude,
            'longitude': checkpoint.longitude
        } for checkpoint in task_data.checkpoints]

        # Создаем новую задачу и связываем ее с пользователем
        new_task = Task(
            country=task_data.country,
            city=task_data.city,
            start_latitude=task_data.start_coordinates.latitude,
            start_longitude=task_data.start_coordinates.longitude,
            checkpoints=serialized_checkpoints,
            description=task_data.description,
            created_by=user_id  # Привязываем задачу к пользователю
        )
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def get_task_by_id(self, task_id: int):
        # Используем joinedload для загрузки связанных данных о создателе и исполнителе
        result = await self.db.execute(
            select(Task).options(joinedload(Task.creator), joinedload(Task.executor)).filter(Task.id == task_id)
        )
        return result.scalars().first()

    async def delete_task(self, task_id: int):
        # Удаляем задачу по её идентификатору
        result = await self.db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        if task:
            await self.db.delete(task)
            await self.db.commit()
            return True
        return False



    async def get_all_tasks(self):
        # Используем select с joinedload для загрузки связанных данных (создатель задачи)
        result = await self.db.execute(
            select(Task).options(joinedload(Task.creator))  # Загружаем связанные данные о создателе
        )
        tasks = result.scalars().all()
        return tasks
    
    async def accept_task(self, task_id: int, executor_id: int):
        # Исполнитель принимает задачу
        result = await self.db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        if not task:
            return None
        task.executor_id = executor_id
        task.status = "in_progress"

        # Генерируем URL видеопотока с использованием WebSocket
        task.stream_url = f"ws://127.0.0.1:8002/ws/video/{task_id}"

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def complete_task(self, task_id: int):
        # Завершить задачу
        result = await self.db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        if task:
            task.status = "completed"
            await self.db.commit()
            return task
        return None