from datetime import datetime, timedelta
import hashlib
import random
import string
from typing import List
from uuid import UUID

from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from apps.users.models import Users, Tokens
from db.dependencies import get_db
from apps.users.schemas import UserCreate


class UsersActions:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db  # произойдет внедрение зависимостей

    def find_by_name(self, name: str) -> Users:
        query = self.db.query(Users)
        return query.filter(Users.name == name).first()

    def find_by_id(self, uuid: UUID) -> Users:
        query = self.db.query(Users)
        return query.filter(Users.id == uuid).first()

    def find_by_email(self, email: EmailStr):
        query = self.db.query(Users)
        return query.filter(Users.email == email).first()

    def all(self, skip: int = 0, max: int = 100) -> List[Users]:
        query = self.db.query(Users)
        return query.offset(skip).limit(max).all()

    def create(self, user: UserCreate) -> Users:
        """ Создает нового пользователя в БД """
        salt = self.get_random_string()
        hashed_password = self.hash_password(user.password, salt)

        db_user = Users(
            name=user.name,
            email=user.email,
            gender=user.gender,
            created_at=user.created_at,
            age=user.age,
            description=user.description,
            is_admin=user.is_admin,
            hashed_password=f"{salt}${hashed_password}",
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_random_string(self, length=12) -> str:
        """ Генерирует случайную строку, использующуюся как соль """
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    def hash_password(self, password: str, salt: str = None) -> str:
        """ Хеширует пароль с солью """
        if salt is None:
            salt = self.get_random_string()
        enc = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100_000)
        return enc.hex()

    def validate_password(self, password: str, hashed_password: str) -> bool:
        """ Проверяет, что хеш пароля совпадает с хешем из БД """
        salt, hashed = hashed_password.split("$")
        return self.hash_password(password, salt) == hashed

    def get_user_by_token(self, token: str):
        """ Возвращает информацию о владельце указанного токена """
        query = self.db.query(Users).join(
            Tokens, Tokens.user_id == Users.id
        ).filter(
            Tokens.token == token,
            Tokens.expires > datetime.now())

        return query.first()

    def create_user_token(self, user_id: int):
        """ Создает токен для пользователя с указанным user_id """
        db_token = Tokens(
            expires=datetime.now() + timedelta(weeks=2),
            user_id=user_id
        )

        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)

        return db_token
