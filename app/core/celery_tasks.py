from abc import ABC, abstractmethod
from celery import Task
from app.celery_app import celery_app
from app.notifications.notification_sender_service import EmailNotificationSender, SMSNotificationSender

class BaseTaskHandler(ABC):
    """
    Абстрактный базовый класс для обработки задач.
    """
    @abstractmethod
    async def handle(self, *args, **kwargs):
        """
        Метод, который должен быть реализован в дочерних классах.
        """
        pass


class EmailTaskHandler(BaseTaskHandler):
    """
    Класс для обработки задач отправки Email.
    """
    def __init__(self, email_sender: EmailNotificationSender):
        self.email_sender = email_sender

    async def handle(self, recipients: list, subject: str, body: str, subtype: str = "plain"):
        """
        Реализация задачи отправки Email.
        """
        await self.email_sender.send(recipients=recipients, subject=subject, body=body, subtype=subtype)


class SMSTaskHandler(BaseTaskHandler):
    """
    Класс для обработки задач отправки SMS.
    """
    def __init__(self, sms_sender: SMSNotificationSender):
        self.sms_sender = sms_sender

    async def handle(self, recipients: list, body: str):
        """
        Реализация задачи отправки SMS.
        """
        await self.sms_sender.send(recipients=recipients, subject=None, body=body)


class CeleryTask(Task):
    """
    Универсальный класс задачи Celery.
    """
    def run(self, handler_class: str, *args, **kwargs):
        """
        Запуск Celery задачи.

        :param handler_class: Полный путь к классу обработчика (например, "app.tasks.EmailTaskHandler").
        :param args: Позиционные аргументы для обработчика.
        :param kwargs: Именованные аргументы для обработчика.
        """
        module_path, class_name = handler_class.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        handler_class = getattr(module, class_name)

        # Инициализируем обработчик задачи и вызываем handle
        handler = handler_class(*args, **kwargs)
        return handler.handle(*args, **kwargs)


# Регистрация универсальной задачи
@celery_app.task(base=CeleryTask)
def execute_task(handler_class: str, *args, **kwargs):
    """
    Универсальная задача Celery.
    """
    return CeleryTask().run(handler_class, *args, **kwargs)