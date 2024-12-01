from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepo
from memeai.db.models.tweet import Tweet


class TweetRepo(BaseRepo[Tweet]):
    def __init__(self):
        super().__init__(Tweet)

    async def get_by_user_id(self, session: AsyncSession, user_id: int) -> List[Tweet]:
        """Get all tweets by user ID."""
        result = await session.execute(select(Tweet).where(Tweet.author_id == user_id))
        return list(result.scalars().all())

    async def get_latest(self, session: AsyncSession, limit: int = 10) -> List[Tweet]:
        """Get latest tweets."""
        result = await session.execute(
            select(Tweet).order_by(Tweet.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self, session: AsyncSession, tweet_type: str, limit: int = 100
    ) -> List[Tweet]:
        """Get tweets by type."""
        query = select(Tweet)
        if tweet_type == "own":
            query = query.where(Tweet.is_own_tweet == True)
        elif tweet_type == "mention":
            query = query.where(Tweet.is_mention == True)
        elif tweet_type == "following":
            query = query.where(Tweet.is_following_tweet == True)

        query = query.order_by(Tweet.created_at.desc()).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
