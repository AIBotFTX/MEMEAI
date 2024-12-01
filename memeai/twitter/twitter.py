import tweepy
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AsyncTwitterClient:
    def __init__(
        self,
        api_key,
        api_secret,
        access_token,
        access_token_secret,
        bearer_token
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token

        # Initialize the Tweepy Client
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            bearer_token=self.bearer_token,
        )

    async def tweet(self, message: str):
        """Send a tweet"""
        tweet = await asyncio.to_thread(self.client.create_tweet, text=message)
        print(f"https://twitter.com/user/status/{tweet.data['id']}")
        return tweet

    async def get_user_info(self, username: Optional[str | int]):
        """Retrieve user information"""
        if isinstance(username, str):
            user = await asyncio.to_thread(
                self.client.get_user, username=username, user_auth=True,
                user_fields=["name,username", "description", "public_metrics"]
            )
        elif isinstance(username, int):
            user = await asyncio.to_thread(
                self.client.get_user, id=username, user_auth=True,
                user_fields=["name,username", "description", "public_metrics"]
            )
        return user

    async def get_user_timeline(self, user_id: int, max_results: int = 5):
        """Retrieve user tweets"""
        tweets = await asyncio.to_thread(
            self.client.get_users_tweets,
            id=user_id,
            max_results=max_results,
            user_auth=True,
        )
        return tweets

    async def get_user_timeline_home(self, max_results: int = 5):
        """
        Retrieve home timeline tweets with expanded tweet information.
        """
        try:
            home_timeline = await asyncio.to_thread(
                self.client.get_home_timeline,
                max_results=max_results,
                user_fields=["username", "name"],
                tweet_fields=["author_id", "created_at"],
                expansions=["author_id"],
                user_auth=True,
            )
            if not home_timeline.data:
                return []

            # Create a map of user data
            users = {user.id: user for user in home_timeline.includes['users']} if 'users' in home_timeline.includes else {}

            # Enhance tweet data with user information
            enhanced_tweets = []
            for tweet in home_timeline.data:
                tweet.author_id = users.get(tweet.author_id)
                enhanced_tweets.append(tweet)

            return enhanced_tweets
        except Exception as e:
            logger.error(f"Error fetching home timeline: {str(e)}")
            raise

    async def get_tweets(self, tweet_id: list[int | str]):
        tweets = await asyncio.to_thread(
            self.client.get_tweets,
            ids=tweet_id,
            user_auth=True,
        )
        return tweets

    async def get_user_mentions(self, user_id: int | str):
        tweets = await asyncio.to_thread(
            self.client.get_users_mentions,
            id=user_id,
            user_auth=True,
            tweet_fields=["author_id", "created_at", "public_metrics", "source"]
        )
        return tweets
