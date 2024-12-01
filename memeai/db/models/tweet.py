from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memeai.db.models.base import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    content: Mapped[str] = mapped_column(String(500))
    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    retweet_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    quote_count: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(100))
    is_own_tweet: Mapped[bool] = mapped_column(Boolean, default=False)
    is_mention: Mapped[bool] = mapped_column(Boolean, default=False)
    is_following_tweet: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="tweets", foreign_keys=[author_id]
    )

    def __repr__(self) -> str:
        return f"<Tweet(id={self.id}, author_id={self.author_id})>"
