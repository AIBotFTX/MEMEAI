from typing import List, Optional
from sqlalchemy import select, and_
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

    async def get_by_content_and_author(
        self, session: AsyncSession, content: str, author_id: int
    ) -> Optional[Tweet]:
        """Get a tweet by its content and author_id."""
        result = await session.execute(
            select(Tweet).where(
                and_(Tweet.content == content, Tweet.author_id == author_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_twitter_id(
        self, session: AsyncSession, twitter_id: str
    ) -> Optional[Tweet]:
        result = await session.execute(select(Tweet).where(Tweet.id == twitter_id))
        return result.scalar_one_or_none()

    async def get_author(
        self, session: AsyncSession, author_id: int
    ) -> Optional[Tweet]:
        """Get a tweet by its content and author_id."""
        result = await session.execute(
            select(Tweet).where(Tweet.author_id == author_id)
        )
        return result.scalar_one_or_none()
