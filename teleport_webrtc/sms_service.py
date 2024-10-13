from twilio.rest import Client
from .core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID
from fastapi.concurrency import run_in_threadpool

# Инициализация клиента Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Функция отправки SMS через Twilio Verify (асинхронная)
async def send_sms(phone_number: str):
    try:
        # Выводим номер телефона для отправки
        print(f"Phone number for sending SMS: {phone_number}")
        
        # Отправка SMS через Twilio Verify API
        verification = await run_in_threadpool(lambda: client.verify
            .v2
            .services(TWILIO_VERIFY_SERVICE_SID)
            .verifications
            .create(to=phone_number, channel='sms'))

        # Возвращаем статус верификации
        return verification.status
    except Exception as e:
        print(f"Ошибка при отправке SMS: {e}")
        return None

# Функция для проверки кода верификации через Twilio Verify (асинхронная)
async def verify_sms_code(phone_number: str, code: str) -> bool:
    try:
        verification_check = await run_in_threadpool(lambda: client.verify
            .v2
            .services(TWILIO_VERIFY_SERVICE_SID)
            .verification_checks
            .create(to=phone_number, code=code))
        
        # Проверяем статус верификации
        return verification_check.status == "approved"
    except Exception as e:
        print(f"Ошибка при проверке кода: {e}")
        return False