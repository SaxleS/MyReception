from .users import User, Token
from .tasks import Task

# Теперь все модели используют один объект Base
from teleport_webrtc.core.database import Base  # Это тот же Base, который вы используете для миграций