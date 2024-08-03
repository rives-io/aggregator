from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for application"""
    debug: bool = False
    db_url: str = 'postgresql+psycopg2://postgres:postgres123@localhost:5432/postgres' # noqa


settings = Settings()
