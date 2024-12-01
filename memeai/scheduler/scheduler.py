from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


class TwitterScheduler:
    def __init__(self, twitter_client, db_service):
        self.scheduler = AsyncIOScheduler()
        self.client = twitter_client
        self.db_service = db_service
        self.username_id = os.getenv("TWITTER_USERNAME")

    async def fetch_and_store_user_timeline(self, username: str, count: int = 10):
        """Fetch user timeline and store in DB"""
        try:
            tweets = await self.client.get_user_timeline(username, count)
            for tweet in tweets:
                await self.db_service.store_tweet(tweet, tweet_type="following")
            logger.info(f"Scheduled task: Fetched and stored timeline for {username}")
        except Exception as e:
            logger.error(f"Scheduler error fetching timeline for {username}: {str(e)}")

    async def fetch_and_store_home_timeline(self, max_count: int = 10):
        """Fetch home timeline and store in DB"""
        try:
            tweets = await self.client.get_user_timeline_home(max_count)
            for tweet in tweets:
                tweet_type = "own" if tweet["author_id"] == self.username_id else "following"
                await self.db_service.store_tweet(tweet, tweet_type=tweet_type)
            logger.info("Scheduled task: Fetched and stored home timeline")
        except Exception as e:
            logger.error(f"Scheduler error fetching home timeline: {str(e)}")

    async def fetch_and_store_mentions(self, count: int = 10):
        """Fetch mentions and store in DB"""
        try:
            mentions = await self.client.get_mentions(count)
            for tweet in mentions:
                await self.db_service.store_tweet(tweet, tweet_type="mention")
            logger.info("Scheduled task: Fetched and stored mentions")
        except Exception as e:
            logger.error(f"Scheduler error fetching mentions: {str(e)}")

    async def update_user_info(self, usernames: list[str]):
        """Update user information in DB"""
        try:
            for username in usernames:
                user = await self.client.get_user_info(username)
                await self.db_service.store_user(user)
            logger.info(f"Scheduled task: Updated info for users: {usernames}")
        except Exception as e:
            logger.error(f"Scheduler error updating user info: {str(e)}")

    def schedule_tasks(self, followed_users: Optional[list[str]] = None):
        """Initialize all scheduled tasks"""
        try:
            # Fetch home timeline every 30 minutes
            self.scheduler.add_job(
                self.fetch_and_store_home_timeline,
                'interval',
                minutes=30,
                kwargs={'max_count': 50},
                id='home_timeline_job'
            )

            # Fetch mentions every 15 minutes
            self.scheduler.add_job(
                self.fetch_and_store_mentions,
                'interval',
                minutes=15,
                kwargs={'count': 30},
                id='mentions_job'
            )

            # If specific users are provided, schedule their timeline fetching
            if followed_users:
                for username in followed_users:
                    self.scheduler.add_job(
                        self.fetch_and_store_user_timeline,
                        'interval',
                        minutes=45,
                        args=[username],
                        kwargs={'count': 30},
                        id=f'user_timeline_{username}'
                    )

                # Update user info every 6 hours
                self.scheduler.add_job(
                    self.update_user_info,
                    'interval',
                    hours=6,
                    kwargs={'usernames': followed_users},
                    id='update_users_job'
                )

            logger.info("All scheduled tasks have been initialized")
        except Exception as e:
            logger.error(f"Error scheduling tasks: {str(e)}")
            raise

    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            raise

    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
            raise

    def get_job_status(self):
        """Get status of all scheduled jobs"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'next_run': job.next_run_time,
                    'function': job.func.__name__,
                    'interval': job.trigger
                })
            return jobs
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            raise
