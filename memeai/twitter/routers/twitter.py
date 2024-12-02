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


@router.post("/get_tweet")
async def get_tweet(tweet_id: int):
    try:
        tweets = await twitter_client.get_tweets(tweet_id=tweet_id)
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


@router.get("/me/")
async def get_me():
    try:
        me = await twitter_client.get_me()
        return {"user_info": me}
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


@router.get("/get_my_mentioned_tweets")
async def get_my_mentioned_tweets():
    try:
        me = twitter_client.client.get_me()
        tweets = await twitter_client.get_user_mentions(me.data.id)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
