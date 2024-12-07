import asyncio

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from app.notifications.notification_sender_service import EmailNotificationSender

async def send_email():
    """
    Функция для отправки тестового email-сообщения.
    """
    email_sender = EmailNotificationSender()
    recipients = ["axle.mov@gmail.com"]  # Замените на нужный email
    subject = "Test Email"
    body = "This is a test email sent using EmailNotificationSender."
    subtype = "plain"

    try:
        await email_sender.send(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=subtype
        )
        print(f"Email successfully sent to {recipients}")
    except Exception as e:
        print(f"Failed to send email: {e}")

asyncio.run(send_email())