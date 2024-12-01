from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import logging
from memeai.twitter.config import settings
from memeai.db.db_service import TwitterDBService

router = APIRouter(
    prefix="/database",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)

db_service = TwitterDBService(settings.construct_sqlalchemy_url)
logger = logging.getLogger(__name__)


@router.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Starting database initialization...")
        await db_service.init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup database connections"""
    try:
        await db_service.cleanup()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


@router.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {"message": "Welcome to MemeAI Twitter API", "version": "1.0.0"}


@router.post("/mock-data")
async def create_mock_data():
    """Create mock data for testing purposes."""
    try:
        async with db_service.get_session() as session:
            # First, cleanup existing data
            logger.info("Cleaning up existing data...")
            await session.execute(text("DELETE FROM tweets"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()

            # Create test users
            users = [
                await db_service.user_repo.create(
                    session,
                    username=f"test_user_{i}",
                    name=f"Test User {i}",
                    followers_count=0,
                    following_count=0,
                    is_following=True,
                )
                for i in range(1, 4)
            ]

            # Create test tweets for each user
            tweets = []
            for user in users:
                user_tweets = [
                    await db_service.tweet_repo.create(
                        session,
                        content=f"Test tweet {j} from {user.username}",
                        author_id=user.id,
                        like_count=0,
                        retweet_count=0,
                        reply_count=0,
                        quote_count=0,
                        source="test",
                        is_own_tweet=False,
                        is_mention=False,
                        is_following_tweet=True,
                    )
                    for j in range(1, 4)
                ]
                tweets.extend(user_tweets)

        return {
            "message": "Mock data created successfully",
            "users_created": len(users),
            "tweets_created": len(tweets),
            "users": [
                {"id": u.id, "username": u.username, "name": u.name} for u in users
            ],
            "tweets": [
                {"id": t.id, "content": t.content, "author_id": t.author_id}
                for t in tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to create mock data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create mock data: {str(e)}"
        )


@router.get("/health")
async def database_health():
    """Check database health."""
    if not await db_service.simple_health_check():
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "message": "Database health check failed"},
        )
    return {"status": "healthy", "message": "Database is running normally"}


@router.get("/stats")
async def database_stats():
    """Get database statistics."""
    return await db_service.get_db_stats()


@router.get("/tweets/latest")
async def get_latest_tweets(limit: int = 10):
    """Get latest tweets."""
    try:
        tweets = await db_service.get_latest_tweets(limit)
        return {
            "count": len(tweets),
            "tweets": [
                {
                    "id": tweet.id,
                    "content": tweet.content,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat(),
                }
                for tweet in tweets
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get latest tweets: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get latest tweets: {str(e)}"
        )


@router.get("/tweets/{tweet_type}")
async def get_tweets_by_type(tweet_type: str, limit: int = 100):
    """Get tweets by type (own, mention, following)."""
    try:
        tweets = await db_service.get_tweets_by_type(tweet_type, limit)
        return {
            "type": tweet_type,
            "count": len(tweets),
            "tweets": [
                {
                    "id": tweet.id,
                    "content": tweet.content,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat(),
                }
                for tweet in tweets
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get tweets by type: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get tweets by type: {str(e)}"
        )
