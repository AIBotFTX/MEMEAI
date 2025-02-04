from pydantic import BaseModel
from typing import List


class Tweet(BaseModel):
    """Tweet data model."""

    id: int
    content: str
    author_id: int
    created_at: str


class TweetsResponse(BaseModel):
    """API response data model."""

    type: str
    count: int
    tweets: List[Tweet]
