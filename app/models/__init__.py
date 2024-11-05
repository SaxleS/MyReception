from .users import User, Token

# Теперь все модели используют один объект Base
from app.core.database import Base  # Это тот же Base, который вы используете для миграций