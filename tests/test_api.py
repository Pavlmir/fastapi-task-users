from typing import Generator, Iterator
from datetime import datetime

import pytest
from anyio.abc import BlockingPortal
from fastapi.testclient import TestClient
from pydantic import EmailStr
from tortoise.contrib.test import finalizer, initializer
from app.models.app_models import UserGender

from app.repositories.repo import UsersRepo
from app.main import app
from app.models import Users


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["app.models"])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope="module")
def blocking_portal(client: TestClient) -> Iterator[BlockingPortal]:
    yield client.portal


def test_check_connect(client: TestClient, blocking_portal: BlockingPortal):  # nosec
    response = client.get("/")
    assert response.status_code == 200, response.text
    salt = "admin"
    hash_password = UsersRepo.hash_password("12345", salt)
    print(hash_password)


def test_create_admin(client: TestClient, blocking_portal: BlockingPortal):  # nosec
    name: str = "user"
    email: EmailStr = "user@user.ru"
    gender: UserGender = "Мужчина"
    created_at: datetime = datetime.now()
    age: int = 30
    description: str = "Пользователь"
    is_admin: bool = True
    is_active: bool = True

    payload = {
        "name": name,
        "email": email,
        "gender": gender,
        "created_at": created_at.isoformat(),
        "age": age,
        "description": description,
        "is_admin": is_admin,
        "is_active": is_active,
    }

    response = client.post("/v1/manager/users/", json=payload)
    data = response.json()
    assert response.status_code == 200, response.text

    async def get_user_by_db():
        admin = await Users.get(id=data.get("id"))
        return admin

    user_admin = blocking_portal.call(get_user_by_db)
    assert user_admin is None
