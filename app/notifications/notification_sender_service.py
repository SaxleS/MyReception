from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi_mail import MessageSchema, FastMail
from app.core.config import SMSClient, conf  # SMSClient для работы с SMS API

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
        """
        Отправка email с настраиваемым содержимым.

        :param recipients: Список email-адресов получателей.
        :param subject: Тема письма.
        :param body: Текст письма.
        :param subtype: Тип сообщения (plain, html).
        """
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=subtype,
        )
        await self.fast_mail.send_message(message)


class SMSNotificationSender(AbstractNotificationSender):
    def __init__(self):
        self.sms_client = SMSClient()

    async def send(self, recipients: List[str], subject: str, body: str, subtype: Optional[str] = None) -> None:
        """
        Отправка SMS.

        :param recipients: Список номеров телефонов.
        :param subject: Не используется для SMS, но включено для совместимости.
        :param body: Текст сообщения.
        :param subtype: Не используется для SMS.
        """
        for recipient in recipients:
            await self.sms_client.send_sms(phone_number=recipient, message=body)