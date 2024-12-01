from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL


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
    def construct_sqlalchemy_url(self) -> str:
        uri = URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )
        return uri.render_as_string(hide_password=False)

    class Config:
        env_file = ".env"


settings = Settings()
