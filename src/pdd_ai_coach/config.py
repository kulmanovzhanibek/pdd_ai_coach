from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    test_database_url: str
    openai_api_key: str
    chat_model: str = "gpt-6-luna"


settings = Settings()
