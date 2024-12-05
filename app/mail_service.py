from fastapi_mail import FastMail, MessageSchema

from app.core.config import conf
from abc import ABC, abstractmethod


class AbstractNotificationSender(ABC):
    @abstractmethod
    async def send(self, recipient: str, activation_code: str) -> None:
        """
        Отправляет уведомление пользователю.
        
        :param recipient: Получатель (email или телефонный номер).
        :param activation_code: Код активации.
        """
        pass







class EmailNotificationSender(AbstractNotificationSender):
    def __init__(self):
        self.fast_mail = FastMail(conf)

    async def send(self, recipient: str, activation_code: str) -> None:
        """
        Отправка кода активации на email.
        
        :param recipient: Email-адрес получателя.
        :param activation_code: Код активации.
        """
        message = MessageSchema(
            subject="MyReception - Activation Code",
            recipients=[recipient],
            body=f"Ваш код активации: {activation_code}",
            subtype="plain",
        )
        await self.fast_mail.send_message(message)





class SMSNotificationSender(AbstractNotificationSender):
    def __init__(self, sms_api_client):
        """
        :param sms_api_client: Клиент для отправки SMS (например, Twilio, Vonage или другой).
        """
        self.sms_api_client = sms_api_client

    async def send(self, recipient: str, activation_code: str) -> None:
        """
        Отправка кода активации по SMS.
        
        :param recipient: Номер телефона получателя.
        :param activation_code: Код активации.
        """
        message = f"Ваш код активации: {activation_code}"
        # Вызов метода отправки сообщения в API
        await self.sms_api_client.send_sms(to=recipient, message=message)





async def send_mail_verification(email: str, activation_code: str):
    message = MessageSchema(
        subject="MyReception",
        recipients=[email],
        body=f"Ваш код активации: {activation_code}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


    