from pydantic import BaseModel


class TweetRequest(BaseModel):
    message: str
