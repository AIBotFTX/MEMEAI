from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepo
from memeai.db.models.users import User


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
