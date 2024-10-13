from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from teleport_webrtc.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # Добавляем поле username
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    country = Column(String)
    city = Column(String)
    age = Column(Integer)
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    device_model = Column(String)
    os_version = Column(String)
    ip_address = Column(String)
    device_time = Column(DateTime)
    activation_code = Column(String, nullable=True)

    # Связь с токенами
    tokens = relationship("Token", back_populates="user")

    # Задачи, созданные пользователем
    created_tasks = relationship("Task", foreign_keys="[Task.created_by]", back_populates="creator")

    # Задачи, в которых пользователь является исполнителем
    tasks = relationship("Task", foreign_keys="[Task.executor_id]", back_populates="executor")

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_type = Column(String, default="bearer")
    user_id = Column(Integer, ForeignKey("users.id"))  # Связь с пользователем
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to the User model
    user = relationship("User", back_populates="tokens")