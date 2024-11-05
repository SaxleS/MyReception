from pydantic import BaseModel
from typing import List, Optional

# Схема для координат
class Coordinates(BaseModel):
    latitude: float
    longitude: float

    class Config:
        orm_mode = True
        from_attributes = True  # Использование from_orm

# Схема для краткой информации о пользователе (создателе задачи)
class CreatorOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
        from_attributes = True  # Использование from_orm

# Схема для создания новой задачи
class TaskCreate(BaseModel):
    country: str
    city: str
    start_coordinates: Coordinates  # Начальные координаты
    checkpoints: List[Coordinates]  # Список ключевых точек
    description: str  # Описание задачи

    class Config:
        orm_mode = True
        from_attributes = True  # Использование from_orm

# Схема для возврата задачи (например, при получении задачи по ID)
class TaskOut(BaseModel):
    id: int  # ID задачи
    country: str
    city: str
    start_coordinates: Coordinates  # Начальные координаты
    checkpoints: List[Coordinates]  # Список ключевых точек
    description: str  # Описание задачи
    stream_url: Optional[str]  # URL видеопотока (если доступен)
    creator: CreatorOut  # Информация о пользователе, который создал задачу

    class Config:
        orm_mode = True
        from_attributes = True  # Использование from_orm