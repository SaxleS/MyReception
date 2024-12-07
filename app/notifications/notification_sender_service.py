from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi_mail import MessageSchema, FastMail
from app.core.config import conf  # SMSClient для работы с SMS API

class AbstractNotificationSender(ABC):
    @abstractmethod
    async def send(self, recipients: List[str], subject: str, body: str, subtype: Optional[str] = "plain") -> None:
        """
        Отправляет уведомление (email или SMS).

        :param recipients: Список получателей.
        :param subject: Тема сообщения.
        :param body: Текст сообщения.
        :param subtype: Тип сообщения (plain, html и т. д.).
        """
        pass


class EmailNotificationSender(AbstractNotificationSender):
    def __init__(self):
        self.fast_mail = FastMail(conf)

    async def send(self, recipients: List[str], subject: str, body: str, subtype: Optional[str] = "plain") -> None:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype,
            )
            await self.fast_mail.send_message(message)
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise


