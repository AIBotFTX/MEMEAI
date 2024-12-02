from typing import Optional
from sqlalchemy import select
from sqlalchemy import cast, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepo
from memeai.db.models.users import User
import logging


class UserRepo(BaseRepo[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> Optional[User]:
        """Get a user by username."""
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_author_id(self, session: AsyncSession, author_id: int) -> Optional[User]:
        logging.info(f"Fetching user with author_id: {author_id}")
        result = await session.execute(select(User).where(User.id == author_id))
        user = result.scalar_one_or_none()
        if user:
            logging.info(f"User found: {user}")
        else:
            logging.warning(f"No user found with author_id: {author_id}")
        return user
