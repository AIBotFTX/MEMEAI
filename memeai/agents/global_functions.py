from memeai.agents.tool_twitter import (
    # parse_source_code,
    search_tweets_with_media,
    get_user_info,
    tweet,
    get_home_timeline,
    put_like,
    retweet,
    unretweet,
    respond_to_mentions,
    reply_to_tweet,
)
from memeai.agents.tools_pumpfun import (
    listen_pumpfun_events,
    create_pumpfun_wallet,
    buy,
    sell,
)

GLOBAL_FUNCTIONS = {
    "search_tweets_with_media": search_tweets_with_media,
    "get_user_info": get_user_info,
    "tweet": tweet,
    "get_home_timeline": get_home_timeline,
    "put_like": put_like,
    "retweet": retweet,
    "unretweet": unretweet,
    "respond_to_mentions": respond_to_mentions,
    "reply_to_tweet": reply_to_tweet,
    "listen_pumpfun_events": listen_pumpfun_events,
    "create_pumpfun_wallet": create_pumpfun_wallet,
    "buy": buy,
    "sell": sell,
}
