import asyncio
from typing import Generator, Iterator

import pytest
from anyio.abc import BlockingPortal
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer
from app.core.db import init_db

from app.repositories.repo import users_repo
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


def test_create_user(client: TestClient, blocking_portal: BlockingPortal):  # nosec
    response = client.post("/users", json={"username": "admin"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "admin"
    assert "id" in data
    user_id = data["id"]

    async def get_user_by_db():
        user = await Users.get(id=user_id)
        return user

    user_obj = blocking_portal.call(get_user_by_db)
    assert user_obj.id == user_id


def test_create_admin(client: TestClient, blocking_portal: BlockingPortal):  # nosec
    response = client.post("/")
    assert response.status_code != 200, response.text

    async def get_user_by_db():
        # user = await users_repo.find_by_name("admin")
        user = await users_repo.get_user_by_token("03d358e7-97cd-4252-b87c-9e7fa2b4b3e6")
        return user

    user_obj = blocking_portal.call(get_user_by_db)
    assert user_obj is None
