# models/tasks.py
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from teleport_webrtc.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    start_latitude = Column(Float, nullable=False)
    start_longitude = Column(Float, nullable=False)
    checkpoints = Column(JSON, nullable=True)
    description = Column(String, nullable=True)

    # Поле для исполнителя задачи
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    executor = relationship("User", foreign_keys=[executor_id], back_populates="tasks")

    # Поле для статуса задачи
    status = Column(String, default="pending")  # Возможные статусы: pending, in_progress, completed

    # Поле для ссылки на видеопоток
    stream_url = Column(String, nullable=True)

    # Поле для идентификатора пользователя, который создал задачу
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")