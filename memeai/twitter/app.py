from fastapi import FastAPI, HTTPException
import logging
from memeai.twitter.routers import database, twitter
from memeai.twitter.models import TweetRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MemeAI Twitter API")
app.include_router(database.router)
app.include_router(twitter.router)


async def _get_or_create_user(session, user_data):
    user = await database.db_service.user_repo.get_by_username(
        session, user_data.username
    )
    if not user:
        user = await database.db_service.user_repo.create(
            session,
            id=user_data.id,
            username=user_data.username,
            name=user_data.name,
            followers_count=user_data.public_metrics.get("followers_count"),
            following_count=user_data.public_metrics.get("following_count"),
            is_following=False
        )
    return user


async def _store_or_update_tweets(session, user_id, tweets):
    """Store or update tweets in the database."""
    stored_tweets = []
    for tweet_data in tweets:
        tweet_id = int(tweet_data.id)

        existing_tweet = await database.db_service.tweet_repo.get_by_id(
            session, tweet_id
        )

        if existing_tweet:
            existing_tweet.content = tweet_data.text
            await session.commit()
            stored_tweets.append(existing_tweet)
        else:
            new_tweet = await database.db_service.tweet_repo.create(
                session,
                id=tweet_id,
                content=tweet_data.text,
                author_id=user_id,
            )
            stored_tweets.append(new_tweet)
    return stored_tweets


@app.get("/integrated/my_timeline")
async def get_and_store_my_timeline(count: int = 10):
    try:
        # Get user details from Twitter
        me_response = await twitter.twitter_client.get_me()
        logging.info(me_response.data.public_metrics)
        user_id = me_response.data.id

        # Retrieve user timeline
        tweets_response = await twitter.twitter_client.get_user_timeline(user_id, count)
        tweets = tweets_response.data
        logger.info(f"Retrieved {len(tweets)} tweets from Twitter for user {user_id}")

        # Process tweets and user in database
        async with database.db_service.get_session() as session:
            user = await _get_or_create_user(session, me_response.data)
            stored_tweets = await _store_or_update_tweets(session, user.id, tweets)

        # Response construction
        return {
            "status": "success",
            "twitter_tweets_retrieved": len(tweets),
            "tweets_stored": len(stored_tweets),
            "tweets": [
                {
                    "id": tweet.id,
                    "content": tweet.content,
                    "author_id": tweet.author_id,
                    "like_counts": tweet.like_count,
                    "retweet_count": tweet.retweet_count,
                    "reply_count": tweet.reply_count,
                    "created_at": tweet.created_at.isoformat(),
                    "quote_count": tweet.quote_count,
                    "source": tweet.source
                }
                for tweet in stored_tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get and store timeline: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get and store timeline: {str(e)}"
        )


@app.get("/integrated/home_timeline")
async def get_and_store_home_timeline(max_count: int = 50):
    """
    Get home timeline from Twitter and store it in the database.
    """
    try:
        # Get tweets from Twitter
        tweets = await twitter.twitter_client.get_user_timeline_home(max_count)
        logger.info(f"Retrieved {len(tweets)} tweets from home timeline")

        # Store tweets in database
        stored_tweets = []
        async with database.db_service.get_session() as session:
            for tweet in tweets:
                # Get or create user for each tweet
                username = tweet.get("author_username", "unknown")
                user = await database.db_service.user_repo.get_by_username(
                    session, username
                )

                if not user:
                    user = await database.db_service.user_repo.create(
                        session,
                        username=username,
                        name=tweet.get("author_name", username),
                        followers_count=0,
                        following_count=0,
                        is_following=True,
                    )

                # Store tweet
                stored_tweet = await database.db_service.tweet_repo.create(
                    session,
                    content=tweet.get("text", ""),
                    author_id=user_id,
                    like_count=tweet.get("like_count", 0),
                    retweet_count=tweet.get("retweet_count", 0),
                    reply_count=tweet.get("reply_count", 0),
                    quote_count=tweet.get("quote_count", 0),
                    source=tweet.get("source", "twitter"),
                    is_own_tweet=False,
                    is_mention=False,
                    is_following_tweet=True,
                )
                stored_tweets.append(stored_tweet)

        return {
            "status": "success",
            "twitter_tweets_retrieved": len(tweets),
            "tweets_stored": len(stored_tweets),
            "tweets": [
                {
                    "id": tweet.id,
                    "content": tweet.content,
                    "author_id": tweet.author_id,
                    "like_counts": tweet.get("like_count", 0),
                    "retweet_count": tweet.get("retweet_count", 0),
                    "reply_count": tweet.get("reply_count", 0),
                    "created_at": tweet.created_at.isoformat(),
                    "quote_count": tweet.get("quote_count", 0),
                    "source": tweet.get("source", "twitter")
                }
                for tweet in stored_tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get and store home timeline: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get and store home timeline: {str(e)}"
        )


@app.post("/integrated/tweet")
async def create_and_store_tweet(request: TweetRequest):
    """
    Create a tweet on Twitter and store it in the database.
    """
    try:
        # Post tweet to Twitter
        tweet_response = await twitter.twitter_client.tweet(request.message)
        logger.info(f"Created tweet on Twitter: {tweet_response}")

        # Get user info (me) from Twitter
        me = await twitter.twitter_client.get_me()
        logger.info(f"Retrieved user info for tweet author")

        # Store tweet in database
        async with database.db_service.get_session() as session:
            # Get or create user
            user = await database.db_service.user_repo.get_by_username(
                session, me.get("username", "unknown")
            )

            if not user:
                user = await database.db_service.user_repo.create(
                    session,
                    username=me.get("username", "unknown"),
                    name=me.get("name", ""),
                    followers_count=me.get("followers_count", 0),
                    following_count=me.get("following_count", 0),
                    is_following=False,
                )

            # Store the tweet
            stored_tweet = await database.db_service.tweet_repo.create(
                session,
                content=request.message,
                author_id=user.id,
                like_count=tweet_response.get("like_count", 0),
                retweet_count=tweet_response.get("retweet_count", 0),
                reply_count=tweet_response.get("reply_count", 0),
                quote_count=tweet_response.get("quote_count", 0),
                source="twitter_api",
                is_own_tweet=True,
                is_mention=False,
                is_following_tweet=False,
            )

            return {
                "status": "success",
                "twitter_response": tweet_response,
                "stored_tweet": {
                    "id": stored_tweet.id,
                    "content": stored_tweet.content,
                    "author_id": stored_tweet.author_id,
                    "created_at": stored_tweet.created_at.isoformat(),
                    "is_own_tweet": stored_tweet.is_own_tweet,
                },
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                },
            }

    except Exception as e:
        logger.error(f"Failed to create and store tweet: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create and store tweet: {str(e)}"
        )
