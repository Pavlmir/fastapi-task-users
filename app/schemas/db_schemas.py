import json
from datetime import datetime
import typing
from enum import Enum

from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, UUID4, Field, validator
import strawberry

from app.models import Users, Tokens
from app.models.app_models import UserGenderType
import app.models.app_models as models

# write db models pydantic here

Users_Pydantic = pydantic_model_creator(Users)
Tokens_Pydantic = pydantic_model_creator(Tokens)


class TokenBasePydantic(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: typing.Optional[str] = "bearer"

    class Config:
        orm_mode = True 
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        """ Конвертирует UUID в hex строку """
        return value.hex


class UserBasePydantic(BaseModel):
    """ 
    Формирует тело ответа с деталями пользователя
    """
    name: str
    email: EmailStr
    gender: UserGenderType
    created_at: datetime
    age: int
    description: str
    is_admin: bool
    is_active: bool

    class Config:
        orm_mode = True  # TL;DR; помогает связать модель со схемой


class UserCreatePydantic(UserBasePydantic):
    """ 
    Проверяется запрос на создание пользователя 
    """
    password: str


class UserUpdate(UserBasePydantic):
    id: int


class UserTokenPydantic(UserBasePydantic):
    """ 
    Пароль никогда не должен быть возвращен в ответе.
    Формирует тело ответа с деталями пользователя и токеном 
    """
    id: int
    token: TokenBasePydantic

    class Config:
        orm_mode = True  # TL;DR; помогает связать модель со схемой


@strawberry.type
class EnumType:
    name: str
    value: str


@strawberry.type
class Query:

    @strawberry.field
    def get_enum(self, name_enum_type: str) -> list[EnumType]:
        result = []
        enum_type = getattr(models, name_enum_type)
        if enum_type and issubclass(enum_type, Enum):
            for item in enum_type:
                result.append(EnumType(name=item.name, value=item.value))

        return result

    @strawberry.field
    def hello(self, name: str) -> str:
        return "Hi" + name


schema_graphql = strawberry.Schema(Query)
