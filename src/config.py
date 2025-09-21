import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    YF_CACHE_TTL_SEC: int = 3600 
    DEBUGGING: bool = os.getenv("")

settings = Settings()
