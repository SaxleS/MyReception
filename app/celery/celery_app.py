from celery import Celery
from app.core.config import BROKER_URL, BACKEND_URL


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