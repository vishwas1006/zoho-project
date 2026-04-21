from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    zoho_client_id: str
    zoho_client_secret: str
    zoho_redirect_uri: str
    groq_api_key: str
    secret_key: str
    database_url: str = "sqlite+aiosqlite:///./chatbot.db"

    class Config:
        env_file = ".env"

settings = Settings()