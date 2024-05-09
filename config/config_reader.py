#  Use pydantic to read .env config instead of self-written parser
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot
    bot_token: str

    # DB
    db_user: str
    db_passw: str
    db_host: str
    db_port: str
    db_name: str

    virustotal_api: str

    max_size_mb: int

    class Config:
        env_file = "config/file.env"
        env_file_encoding = "utf-8"


config = Settings()
