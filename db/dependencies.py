from functools import lru_cache
from sqlalchemy.orm import Session

from core import config
from db import database


# Вызывается по время внедрения зависимости
def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Возврат существующего экземпляра DBSettings вместо создания нового
@lru_cache
def get_db_settings() -> config.DBSettings:
    return config.DBSettings()
