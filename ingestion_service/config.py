from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://hydrowatch:changeme@localhost:5432/hydrowatch"

    class Config:
        env_file = ".env"


settings = Settings()
