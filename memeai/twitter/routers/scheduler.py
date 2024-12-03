from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
import asyncio
import logging
from functools import partial

from memeai.twitter.routers.integrated import (
    get_and_store_my_timeline,
    get_and_store_home_timeline,
    create_and_store_tweet,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

# Initialize scheduler but don't start it yet
scheduler = AsyncIOScheduler()

# Use AsyncIOScheduler instead of BackgroundScheduler
# scheduler = AsyncIOScheduler()
# scheduler.start()


async def scheduled_my_timeline_task(count: int = 10):
    try:
        logger.info("Executing scheduled task: Fetch My Timeline")
        await get_and_store_my_timeline(count=count)
    except Exception as e:
        logger.error(f"Error during scheduled My Timeline task: {e}")


async def scheduled_home_timeline_task(max_count: int = 50):
    try:
        logger.info("Executing scheduled task: Fetch Home Timeline")
        await get_and_store_home_timeline(max_count=max_count)
    except Exception as e:
        logger.error(f"Error during scheduled Home Timeline task: {e}")


async def scheduled_create_tweet_task(message: str):
    try:
        logger.info(f"Executing scheduled task: Create Tweet with message '{message}'")
        await create_and_store_tweet({"message": message})
    except Exception as e:
        logger.error(f"Error during scheduled Create Tweet task: {e}")


@router.post("/add_my_timeline_job")
async def add_my_timeline_job(interval: int = 60, count: int = 10):
    try:
        scheduler.add_job(
            scheduled_my_timeline_task,
            "interval",
            seconds=interval,
            id="my_timeline_job",
            kwargs={"count": count},
            replace_existing=True,
        )
        return {
            "status": "success",
            "message": "My Timeline job scheduled successfully.",
        }
    except Exception as e:
        logger.error(f"Failed to schedule My Timeline job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_home_timeline_job")
async def add_home_timeline_job(interval: int = 60, max_count: int = 50):
    try:
        scheduler.add_job(
            scheduled_home_timeline_task,
            "interval",
            seconds=interval,
            id="home_timeline_job",
            kwargs={"max_count": max_count},
            replace_existing=True,
        )
        return {
            "status": "success",
            "message": "Home Timeline job scheduled successfully.",
        }
    except Exception as e:
        logger.error(f"Failed to schedule Home Timeline job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_tweet_job")
async def add_tweet_job(interval: int = 3600, message: str = "Scheduled Tweet"):
    try:
        scheduler.add_job(
            scheduled_create_tweet_task,
            "interval",
            seconds=interval,
            id="tweet_job",
            kwargs={"message": message},
            replace_existing=True,
        )
        return {"status": "success", "message": "Tweet job scheduled successfully."}
    except Exception as e:
        logger.error(f"Failed to schedule Tweet job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove_job/{job_id}")
async def remove_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"status": "success", "message": f"Job {job_id} removed successfully."}
    except JobLookupError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    except Exception as e:
        logger.error(f"Failed to remove job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list_jobs")
async def list_jobs():
    jobs = [
        {
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger),
        }
        for job in scheduler.get_jobs()
    ]
    return {"status": "success", "jobs": jobs}


# Shutdown handler
@router.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
