from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Twitter API Credentials
    API_SECRET: str
    API_KEY_SECRET: str
    BEARER_TOKEN: str
    ACCESS_TOKEN: str
    ACCESS_TOKEN_SECRET: str
    CLIENT_ID: str
    CLIENT_SECRET: str

    # Database Configuration
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
