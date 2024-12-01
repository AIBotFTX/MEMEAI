from memeai.twitter.twitter import AsyncTwitterClient
from memeai.twitter.config import settings
from fastapi import APIRouter, HTTPException
from memeai.twitter.models import TweetRequest
import logging

router = APIRouter(
    prefix="/twitter",
    tags=["twitter"],
    responses={404: {"description": "Not found"}},
)
twitter_client = AsyncTwitterClient(
    api_key=settings.API_SECRET,
    api_secret=settings.API_KEY_SECRET,
    access_token=settings.ACCESS_TOKEN,
    access_token_secret=settings.ACCESS_TOKEN_SECRET,
    bearer_token=settings.BEARER_TOKEN,
)

logger = logging.getLogger(__name__)


@router.post("/tweet/")
async def create_tweet(request: TweetRequest):
    try:
        tweet = await twitter_client.tweet(request.message)
        return {"status": "success", "tweet": tweet}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_tweets")
async def get_tweets(tweet_ids: list[int | str]):
    try:
        tweets = await twitter_client.get_tweets(tweet_id=tweet_ids)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{username}")
async def get_user_info(username: str):
    try:
        user = await twitter_client.get_user_info(username)
        return {"user_info": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{username}/timeline/")
async def get_user_timeline(username: str, count: int = 1):
    try:
        tweets = await twitter_client.get_user_timeline(username, count)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/home_timeline")
async def get_user_timeline_home(max_count: int):
    try:
        tweets = await twitter_client.get_user_timeline_home(max_count)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_mentioned_tweets")
async def get_mentioned_tweets(id: int | str):
    try:
        tweets = await twitter_client.get_user_mentions(id)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
