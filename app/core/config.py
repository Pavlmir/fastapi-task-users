import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """
    Settings
    """

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost"]  # type: ignore

    ID_MIN: int = 1

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DATABASE_URI: Optional[PostgresDsn] = None

    NODOC: bool = False
    API_ROOT_URL: str = ""

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls,
        value: Optional[str],
        values: Dict[str, Any],  # noqa: N805, WPS110
    ) -> str:
        if isinstance(value, str):
            return value

        return PostgresDsn.build(
            scheme="postgres",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path="/{0}".format(values.get("DB_NAME")),
        )

    class Config(object):
        env_prefix = ""  # prefix for env variables, defaults to no prefix, i.e. ""
        case_sensitive = True

#TODO
path_input = Path(__file__).parent.parent.parent / ".env"
os.environ["SECRETS_PATH"] = str(path_input)

# Load secrets from file on SECRETS_PATH in dotenv format
settings = Settings(_env_file=os.environ.get("SECRETS_PATH"))
