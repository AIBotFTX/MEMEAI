from fastapi import FastAPI
from memeai.twitter.routers import database, twitter, integrated, scheduler
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup: Initialize scheduler before the app starts
    loop = asyncio.get_event_loop()
    if not scheduler.scheduler.running:
        scheduler.scheduler.configure(event_loop=loop)
        scheduler.scheduler.start()

    yield

    # Cleanup: Shutdown scheduler when the app stops
    if scheduler.scheduler.running:
        scheduler.scheduler.shutdown()


app = FastAPI(title="MemeAI Twitter API", lifespan=lifespan)

# Include routers
app.include_router(database.router)
app.include_router(twitter.router)
app.include_router(integrated.router)
app.include_router(scheduler.router)
