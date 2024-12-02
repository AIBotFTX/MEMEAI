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


@router.delete("/clear")
async def clear_database():
    """Remove all data from the database."""
    try:
        async with db_service.get_session() as session:
            logger.info("Clearing all database data...")

            # Delete data from all tables
            # Note: Order matters due to foreign key constraints
            await session.execute(text("DELETE FROM tweets"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()

            logger.info("Database cleared successfully")

            return {
                "status": "success",
                "message": "All database data has been removed",
                "tables_cleared": ["tweets", "users"],
            }

    except Exception as e:
        logger.error(f"Failed to clear database: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to clear database: {str(e)}"
        )


@router.post("/mock-data")
async def create_mock_data():
    """Create or update mock data for testing purposes."""
    try:
        async with db_service.get_session() as session:
            users = []
            tweets = []

            # Create or update test users
            for i in range(1, 4):
                username = f"test_user_{i}"
                # Try to get existing user
                user = await db_service.user_repo.get_by_username(session, username)

                if user:
                    # Update existing user
                    user.name = f"Test User {i}"
                    user.followers_count = 0
                    user.following_count = 0
                    user.is_following = True
                    await session.commit()
                else:
                    # Create new user
                    user = await db_service.user_repo.create(
                        session,
                        username=username,
                        name=f"Test User {i}",
                        followers_count=0,
                        following_count=0,
                        is_following=True,
                    )
                users.append(user)

            # Create or update test tweets for each user
            for user in users:
                for j in range(1, 4):
                    content = f"Test tweet {j} from {user.username}"
                    # Try to find existing tweet with same content and author
                    existing_tweet = (
                        await db_service.tweet_repo.get_by_content_and_author(
                            session, content=content, author_id=user.id
                        )
                    )

                    if existing_tweet:
                        # Update existing tweet
                        existing_tweet.like_count = 0
                        existing_tweet.retweet_count = 0
                        existing_tweet.reply_count = 0
                        existing_tweet.quote_count = 0
                        existing_tweet.source = "test"
                        existing_tweet.is_own_tweet = False
                        existing_tweet.is_mention = False
                        existing_tweet.is_following_tweet = True
                        await session.commit()
                        tweets.append(existing_tweet)
                    else:
                        # Create new tweet
                        new_tweet = await db_service.tweet_repo.create(
                            session,
                            content=content,
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
                        tweets.append(new_tweet)

        return {
            "message": "Mock data created/updated successfully",
            "users_processed": len(users),
            "tweets_processed": len(tweets),
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "name": u.name,
                }
                for u in users
            ],
            "tweets": [
                {
                    "id": t.id,
                    "content": t.content,
                    "author_id": t.author_id,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to create/update mock data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create/update mock data: {str(e)}"
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
                    "like_count": tweet.like_count
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


@router.get("/tweets/{author_id}")
async def get_tweets_by_author_id(author_id: int):
    """Get tweets by type (own, mention, following)."""
    try:
        tweets = await db_service.get_by_author_id(author_id)
        return {
            "author_id": author_id,
            "count": len(tweets),
            "tweets": [
                {
                    "id": tweet.id,
                    "content": tweet.content,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat(),
                    "likes": tweet.like_count
                }
                for tweet in tweets
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get tweets by type: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get tweets by type: {str(e)}"
        )


@router.get("/user/{author_id}")
async def get_user_by_author_id(author_id: int):
    try:
        user = await db_service.get_by_author_id(author_id)
        if user:
            return {
                "author_id": author_id,
                "username": user.username,
                "name": user.name,
                "followers": user.followers_count,
                "following": user.following_count
            }
        else:
            return {
                "author_id": None,
                "username": None,
                "name": None,
                "followers": None,
                "following": None
            }

    except Exception as e:
        logger.error(f"Failed to get user by author_id: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get tweets by type: {str(e)}"
        )
