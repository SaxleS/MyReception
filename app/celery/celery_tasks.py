from celery import shared_task
from app.notifications.notification_sender_service import EmailNotificationSender
import asyncio

@shared_task
def send_verification_email_task(recipients: list, subject: str, body: str, subtype: str = "plain"):
    email_sender = EmailNotificationSender()

    async def send_email():
        await email_sender.send(recipients, subject, body, subtype)

    asyncio.run(send_email())