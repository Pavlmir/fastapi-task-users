from db.settings import DBSettings

configs = [DBSettings]


class Settings(*configs):
    API_URL: str = "/api/v1"


settings = Settings()