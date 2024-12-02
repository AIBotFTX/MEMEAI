from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, func
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import Dict, Any, AsyncGenerator, Optional

from memeai.db.models.base import Base
from memeai.db.repo.tweet import TweetRepo
from memeai.db.repo.users import UserRepo
from memeai.db.models.tweet import Tweet
from memeai.db.models.users import User

logger = logging.getLogger(__name__)


class TwitterDBService:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True, pool_pre_ping=True)
        self.async_session = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.user_repo = UserRepo()
        self.tweet_repo = TweetRepo()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a database session with automatic cleanup."""
        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            await session.close()

    async def init_db(self) -> None:
        """Initialize database tables."""
        try:
            logger.info("Creating database tables...")
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    async def simple_health_check(self) -> bool:
        """Perform a simple database health check."""
        try:
            async with self.async_session() as session:
                await session.execute(text("SELECT 1"))
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def cleanup(self) -> None:
        """Cleanup database connections."""
        try:
            await self.engine.dispose()
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup database: {str(e)}")
            raise

    async def store_tweet(
        self, tweet_data: dict, tweet_type: str = "following"
    ) -> Optional[Tweet]:
        """Store a tweet using the tweet repository."""
        async with self.get_session() as session:
            tweet_dict = {
                "id": tweet_data["id"],
                "content": tweet_data["text"],
                "created_at": datetime.strptime(
                    tweet_data["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "author_id": tweet_data["author_id"],
                "like_count": tweet_data.get("public_metrics", {}).get("like_count", 0),
                "retweet_count": tweet_data.get("public_metrics", {}).get(
                    "retweet_count", 0
                ),
                "reply_count": tweet_data.get("public_metrics", {}).get(
                    "reply_count", 0
                ),
                "quote_count": tweet_data.get("public_metrics", {}).get(
                    "quote_count", 0
                ),
                "source": tweet_data.get("source", ""),
                "is_own_tweet": tweet_type == "own",
                "is_mention": tweet_type == "mention",
                "is_following_tweet": tweet_type == "following",
            }

            return await self.tweet_repo.create(session, **tweet_dict)

    async def store_user(self, user_data: dict) -> Optional[User]:
        """Store a user using the user repository."""
        async with self.get_session() as session:
            user_repo = UserRepo(session)

            user_dict = {
                "id": user_data["id"],
                "username": user_data["username"],
                "name": user_data["name"],
                "followers_count": user_data["public_metrics"]["followers_count"],
                "following_count": user_data["public_metrics"]["following_count"],
                "is_following": True,
                "last_updated": datetime.utcnow(),
            }

            return await user_repo.create(**user_dict)

    async def get_tweets_by_type(self, tweet_type: str, limit: int = 100):
        """Get tweets by type using the tweet repository."""
        async with self.get_session() as session:
            return await self.tweet_repo.get_by_type(session, tweet_type, limit)

    async def get_latest_tweets(self, limit: int = 10):
        """Get latest tweets using the tweet repository."""
        async with self.get_session() as session:
            return await self.tweet_repo.get_latest(session, limit)

    async def get_by_author_id(self, author_id: int):
        async with self.get_session() as session:
            user = await self.user_repo.get_by_author_id(session, author_id)
            if user is None:
                logging.warning(f"User with author_id {author_id} not found.")
            else:
                logging.info(f"User found: {user.username}")
            return user

    async def get_db_stats(self) -> Dict[str, Any]:
        """Get database statistics using repositories."""
        try:
            async with self.get_session() as session:
                # Use the existing repo instances instead of creating new ones
                tweets = await self.tweet_repo.get_all(
                    session
                )  # Pass session to get_all
                users = await self.user_repo.get_all(session)  # Pass session to get_all

                return {
                    "status": "healthy",
                    "tweet_count": len(tweets),
                    "user_count": len(users),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
