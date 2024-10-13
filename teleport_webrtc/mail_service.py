from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .core.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_STARTTLS, MAIL_SSL_TLS

# Конфигурация для подключения к почтовому серверу
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)

async def send_mail_verification(email: str, activation_code: str):
    message = MessageSchema(
        subject="Ваш код активации",
        recipients=[email],
        body=f"Ваш код активации: {activation_code}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


    