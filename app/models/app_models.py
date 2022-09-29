from tortoise import fields

from app.models.base_models import IdDBModel
from uuid import uuid4

# from db.database import Model
from enum import Enum


class UserErrorsModel(str, Enum):
    user_not_found = "Account is not found."
    email_exist = "Email already registered."


class UserGender(str, Enum):
    male = "Мужчина"
    female = "Женщина"
    other = "Другой"


class Users(IdDBModel):
    name = fields.CharField(max_length=255, unique=True)
    gender = fields.CharEnumField(enum_type=UserGender, default="Другой")
    email = fields.CharField(max_length=100, unique=True, index=True)
    hashed_password = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    age = fields.SmallIntField()
    description = fields.TextField()
    is_admin = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)

    def __str__(self):
        return self.name


class Tokens(IdDBModel):
    token = fields.UUIDField(index=True, default=uuid4)
    expires = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField("models.Users", related_name="user_id")
