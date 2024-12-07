from celery import Celery

# Настройки Celery
BROKER_URL = "redis://localhost:6379/0"  # Укажите адрес брокера
BACKEND_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "test_app",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

# Настройка маршрутов задач
celery_app.conf.task_routes = {
    "tasks.*": {"queue": "default"},
}

# Автоматический поиск задач
celery_app.autodiscover_tasks(["app.celery.celery_tasks"])