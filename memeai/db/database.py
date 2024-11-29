from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, BigInteger

Base = declarative_base()


class Tweet(Base):
    __tablename__ = "tweets"
    
    id = Column(BigInteger, primary_key=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True))
    author_id = Column(BigInteger)
    like_count = Column(Integer, default=0)
    retweet_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    source = Column(String, nullable=True)
    is_own_tweet = Column(Boolean, default=False)
    is_mention = Column(Boolean, default=False)
    is_following_tweet = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String)
    name = Column(String)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    is_following = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True))
