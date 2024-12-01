import os
from dotenv import load_dotenv

load_dotenv()


def get_database_url():
    return (
        f"postgresql+asyncpg://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
