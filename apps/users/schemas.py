from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4, Field, validator

from apps.users.models import UserGender


class TokenBase(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        orm_mode = True 
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        """ Конвертирует UUID в hex строку """
        return value.hex


class UserBase(BaseModel):
    """ 
    Формирует тело ответа с деталями пользователя
    """
    name: str
    email: EmailStr
    gender: UserGender
    created_at: datetime
    age: int
    description: str
    is_admin: bool
    is_active: bool

    class Config:
        orm_mode = True  # TL;DR; помогает связать модель со схемой


class UserCreate(UserBase):
    """ 
    Проверяется запрос на создание пользователя 
    """
    password: str


class UserUpdate(UserBase):
    id: int


class UserToken(UserBase):
    """ 
    Пароль никогда не должен быть возвращен в ответе.
    Формирует тело ответа с деталями пользователя и токеном 
    """
    id: int
    token: TokenBase = {}

    class Config:
        orm_mode = True  # TL;DR; помогает связать модель со схемой
