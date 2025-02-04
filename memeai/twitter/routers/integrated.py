from fastapi import APIRouter, HTTPException
import logging
from memeai.twitter.routers import database, twitter
from memeai.twitter.models import TweetRequest
from letta import create_client
from memeai.twitter.routers.letta_agent import generate_tweet_content
# from memeai.twitter.client import client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrated", tags=["Integrated"])


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
            is_following=False,
        )
    return user


async def _store_or_update_tweets(session, user_id, tweets):
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
                is_own_tweet=True,
                is_following_tweet=False,
            )
            stored_tweets.append(new_tweet)
    return stored_tweets


@router.get("/my_timeline")
async def get_and_store_my_timeline(count: int = 10):
    try:
        me_response = await twitter.twitter_client.get_me()
        logger.info(me_response.data.public_metrics)
        user_id = me_response.data.id

        tweets_response = await twitter.twitter_client.get_user_timeline(user_id, count)
        tweets = tweets_response.data
        logger.info(f"Retrieved {len(tweets)} tweets from Twitter for user {user_id}")

        async with database.db_service.get_session() as session:
            user = await _get_or_create_user(session, me_response.data)
            stored_tweets = await _store_or_update_tweets(session, user.id, tweets)

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
                    "source": tweet.source,
                }
                for tweet in stored_tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get and store timeline: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get and store timeline: {str(e)}"
        )


@router.get("/home_timeline")
async def get_and_store_home_timeline(max_count: int = 50):
    try:
        # Retrieve tweets from the home timeline
        tweets = await twitter.twitter_client.get_user_timeline_home(max_count)
        logger.info(f"Retrieved {len(tweets)} tweets from Twitter")

        async with database.db_service.get_session() as session:
            stored_tweets = []
            for tweet in tweets:
                # Extract author details
                author = tweet.get("author_id")
                if not author or "id" not in author:
                    logger.warning(
                        f"Missing author information for tweet {tweet.get('id')}"
                    )
                    continue

                author_id = int(author["id"])  # Ensure `author_id` is an integer
                username = author.get("username", "unknown")
                name = author.get("name", username)

                # Retrieve or create the user in the database
                user = await database.db_service.user_repo.get_by_username(
                    session, username
                )
                if not user:
                    user = await database.db_service.user_repo.create(
                        session,
                        id=author_id,
                        username=username,
                        name=name,
                        followers_count=0,
                        following_count=0,
                        is_following=True,
                    )

                # Create or update the tweet in the database
                public_metrics = tweet.get("public_metrics", {})
                stored_tweet = await database.db_service.tweet_repo.create(
                    session,
                    id=tweet.get("id", 0),
                    content=tweet.get("text", ""),
                    author_id=user.id,
                    like_count=public_metrics.get("like_count", 0),
                    retweet_count=public_metrics.get("retweet_count", 0),
                    reply_count=public_metrics.get("reply_count", 0),
                    quote_count=public_metrics.get("quote_count", 0),
                    source="twitter",
                    is_own_tweet=False,
                    is_mention=False,
                    is_following_tweet=True,
                )
                stored_tweets.append(stored_tweet)

        # Return the response with stored tweets
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
                    "source": tweet.source,
                }
                for tweet in stored_tweets
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get and store timeline: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get and store timeline: {str(e)}"
        )


@router.post("/tweet")
async def create_and_store_tweet(request: TweetRequest):
    try:
        # Create tweet on Twitter
        answer = await generate_tweet_content(message=request.message)
        tweet_response = await twitter.twitter_client.tweet(answer)
        logger.info(f"Tweet response type: {type(tweet_response)}")
        logger.info(f"Tweet response content: {tweet_response}")

        # Get user info
        me = await twitter.twitter_client.get_me()
        logger.info(f"Retrieved user info for tweet author {me.data.id}")

        async with database.db_service.get_session() as session:
            # Get or create user
            user = await database.db_service.user_repo.get_by_username(
                session, me.data.username
            )

            tweet_id = int(tweet_response.data["id"])

            # Store the tweet
            stored_tweet = await database.db_service.tweet_repo.create(
                session,
                id=tweet_id,
                content=answer,
                author_id=int(me.data.id),
                like_count=0,
                retweet_count=0,
                reply_count=0,
                quote_count=0,
                source="my tweet",
                is_own_tweet=True,
                is_mention=False,
                is_following_tweet=False,
            )

            return {
                "status": "success",
                "twitter_response": {"id": tweet_id, "text": answer},
                "stored_tweet": {
                    "id": tweet_id,
                    "content": answer,
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
        logger.error(f"Tweet response type: {type(tweet_response)}")
        logger.error(f"Tweet response content: {tweet_response}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create and store tweet: {str(e)}"
        )
