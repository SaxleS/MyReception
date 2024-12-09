import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from fastapi import FastAPI

load_dotenv()

app = FastAPI(
    title="MyReception",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# Celery
BROKER_URL = os.getenv("CELERY_BROKER_URL")
BACKEND_URL = os.getenv("CELERY_BACKEND_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
DATABASE_URL = os.getenv("DATABASE_URL")
SMS_API_KEY = os.getenv("SMS_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

CHAT_MONGO_URI = os.getenv("CHAT_MONGO_URI")
CHAT_DATABASE_NAME = os.getenv("CHAT_DATABASE_NAME")

# Конфигурация почтового сервера
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_STARTTLS = True
MAIL_SSL_TLS = False
USE_CREDENTIALS = True

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS,
)