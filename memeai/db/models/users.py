from datetime import datetime
from sqlalchemy import String, DateTime, Integer, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memeai.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    is_following: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Define the relationship to Tweet
    tweets: Mapped[list["Tweet"]] = relationship(
        "Tweet", back_populates="user", foreign_keys="[Tweet.author_id]"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
