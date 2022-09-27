from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Enum as EnumSQL
from sqlalchemy.dialects.postgresql import UUID

from db.database import Model
from enum import Enum


class UserErrorsModel(str, Enum):
    user_not_found = "Account is not found."
    email_exist = "Email already registered."


class UserGender(str, Enum):
    male = "Мужчина"
    female = "Женщина"
    other = "Другой"


class Users(Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    gender = Column(EnumSQL(UserGender), nullable=False,
                    default=UserGender.other.value)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String())
    created_at = Column(DateTime())
    age = Column(Integer())
    description = Column(String(100), default="")
    is_admin = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=False)


class Tokens(Model):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid4, index=True)
    expires = Column(DateTime())
    user_id = Column(Integer, ForeignKey("users.id"))