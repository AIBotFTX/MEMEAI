from fastapi import FastAPI
import logging

from memeai.twitter.routers import database, twitter

app = FastAPI(title="MemeAI Twitter API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(database.router)
app.include_router(twitter.router)
