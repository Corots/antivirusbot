#  Use pydantic to read .env config instead of self-written parser 
from pydantic import BaseSettings


class Settings(BaseSettings):
    #Bot
    session_name : str
    api_id  : int
    api_hash : str

    class Config:
        env_file = 'config/test_file.env'
        env_file_encoding = 'utf-8'


test_config = Settings()