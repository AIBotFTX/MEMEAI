from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    REDIS_PASSWORD: str
    REDIS_SSL: str
    REDIS_TIMEOUT: str
    REDIS_RETRY_ON_TIMEOUT: str
    REDIS_MAX_CONNECTIONS: str
    
    EMBEDDINGS_SIZE: int

    @property
    def construct_redis_url(self) -> str:
        # Construct the Redis URL
        uri = URL.create(
            drivername="redis",
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=int(self.REDIS_PORT),
            database=self.REDIS_DB,
        )
        return uri.render_as_string(hide_password=False)

    class Config:
        env_file = ".env"


settings = Settings()
