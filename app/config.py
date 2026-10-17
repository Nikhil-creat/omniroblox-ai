from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str = ""
    api_key: str = ""  # optional: if set, clients must send X-API-Key
    redis_url: str = "redis://redis:6379/0"
    qdrant_url: str = "http://qdrant:6333"
    groq_base: str = "https://api.groq.com/openai/v1"

settings = Settings()
