from celery import Celery
from app.core.config import BACKEND_URL, BROKER_URL

celery_app = Celery(
    "notifications",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

# Настройка маршрутов задач
celery_app.conf.task_routes = {
    "app.tasks.task_celery.*": {"queue": "notifications"},
}

# Автоматический поиск задач в указанных модулях
celery_app.conf.task_default_queue = "default"
celery_app.autodiscover_tasks(["app.tasks"])