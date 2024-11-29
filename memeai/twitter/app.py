from fastapi import FastAPI
from memeai.twitter.routers import database, twitter, integrated, scheduler

app = FastAPI(title="MemeAI Twitter API")
app.include_router(database.router)
app.include_router(twitter.router)
app.include_router(integrated.router)
app.include_router(scheduler.router)
