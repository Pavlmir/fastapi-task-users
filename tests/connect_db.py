from datetime import datetime

from tortoise import Tortoise, fields, run_async

from app.models import Users
from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URI},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def run():
    await Tortoise.init(
        db_url=settings.DATABASE_URI,
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas(safe=True)

    admin = await Users.filter(email="admin@admin.ru").first()
    if not admin:
        await Users.create(
            name="admin",
            email="admin@admin.ru",
            gender="Другой",
            created_at=datetime.now(),
            age=30,
            description="Администратор системы",
            is_admin=True,
            is_active=True,
            hashed_password="admin$2bff24a01f93f9fca21d60694a08eee7d0fde73082dd92dcd6f4d61f3c230ada")


if __name__ == "__main__":
    run_async(run())
