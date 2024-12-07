from fastapi_mail import FastMail, MessageSchema

from app.core.config import conf
from abc import ABC, abstractmethod





class AbstractNotificationSender(ABC):
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str) -> None:
        """
        Отправляет уведомление пользователю.

        :param recipient: Email-адрес получателя.
        :param subject: Тема письма.
        :param body: Текст письма.
        """
        pass


class EmailNotificationSender(AbstractNotificationSender):
    def __init__(self):
        self.fast_mail = FastMail(conf)

    async def send(self, recipient: str, subject: str, body: str) -> None:
        """
        Отправка письма на email.

        :param recipient: Email-адрес получателя.
        :param subject: Тема письма.
        :param body: Текст письма.
        """
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=body,
            subtype="plain",
        )
        await self.fast_mail.send_message(message)







    