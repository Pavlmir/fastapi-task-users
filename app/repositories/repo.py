from datetime import datetime, timedelta
import hashlib
import random
import string
from typing import Optional

from tortoise import Tortoise
from pypika import Query, Tables

from app.models.app_models import Users, Tokens
from app.schemas.db_schemas import UserCreatePydantic, Users_Pydantic, UserTokenPydantic, Tokens_Pydantic
from app.repositories.base_repo import BaseRepository  # noqa: F401


class UsersActions(BaseRepository):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create(self, user: UserCreatePydantic) -> Users:
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
        await db_user.save()

        return db_user

    @staticmethod
    def get_random_string(length=12) -> str:
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

    @staticmethod
    async def get_user_by_token(token: str) -> Optional[UserTokenPydantic]:
        """ Возвращает информацию о владельце указанного токена """
        user = None
        users, tokens = Tables("users", "tokens")
        query = Query \
            .from_(users) \
            .join(tokens) \
            .on(users.id == tokens.user_id) \
            .select(
                users.id,
                users.name,
                users.email,
                users.gender,
                users.created_at,
                users.age,
                users.description,
                users.is_admin,
                users.is_active,
                tokens.token.as_("access_token"),
                tokens.expires,
                    ) \
            .where((tokens.token == token) & (tokens.expires > datetime.now()))

        conn = Tortoise.get_connection("default")
        data = await conn.execute_query_dict(str(query))
        if data:
            row = data[0]
            row["token"] = {
                "access_token": row.get("access_token"),
                "expires": row.get("expires")
            }
            user = UserTokenPydantic(**row)

        return user


class TokensActions(BaseRepository):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    async def create(user_id: int):
        """ Создает токен для пользователя с указанным user_id """
        token = await Tokens.create(
            expires=datetime.now() + timedelta(weeks=2),
            user_id=user_id
        )

        return token


UsersRepo = UsersActions(Users, Users_Pydantic)
TokensRepo = TokensActions(Tokens, Tokens_Pydantic)
