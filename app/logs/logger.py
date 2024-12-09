import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from .config import LogConfig
from .models import LogEntry


config = LogConfig()

class MongoDBLogHandler(logging.Handler):
    def __init__(self, mongo_uri: str, database_name: str, collection_name: str):
        super().__init__()
        self.queue = asyncio.Queue()  # Очередь для логов
        self.client = AsyncIOMotorClient(mongo_uri)
        self.collection = self.client[database_name][collection_name]
        self._is_running = True

        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self._process_queue())

    def emit(self, record):

        log_entry = LogEntry(
            level=record.levelname,
            message=record.msg,
            module=record.module,
        )

        self.queue.put_nowait(log_entry)

    async def _process_queue(self):
        while self._is_running:
            try:

                log_entry = await self.queue.get()
                await self.collection.insert_one(log_entry.dict())
            except Exception as e:
                print(f"Ошибка записи лога в MongoDB: {e}")

    def close(self):
        self._is_running = False
        super().close()


class Logger:
    @staticmethod
    def setup_logger():
        log_handler = MongoDBLogHandler(
            mongo_uri=config.MONGO_URI,
            database_name=config.DATABASE_NAME,
            collection_name=config.COLLECTION_NAME,
        )
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("app_logger")
        logger.addHandler(log_handler)
        return logger