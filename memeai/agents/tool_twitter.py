from textwrap import dedent
import inspect


def parse_source_code(func) -> str:
    """Parse the source code of a function and remove indendation"""

    source_code = dedent(inspect.getsource(func))
    return source_code


def search_tweets_with_media(query: str) -> str:
    """
    Search for tweets containing a specified query, including media, author, and creation time details.

    Args:
        query (str): The search query to find relevant tweets.

    Returns:
        str: A formatted string containing tweet details, including text, author, time, and image URLs.
    """
    # from memeai.twitter.config import settings
    import tweepy
    from memeai.twitter.config import settings

    client = tweepy.Client(
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )
    response = client.search_recent_tweets(
        query=query,
        expansions=["attachments.media_keys", "author_id"],
        media_fields=["url"],
        tweet_fields=["created_at"],
    )

    tweets = response.data
    includes = response.includes

    # Retrieve users and media objects
    users = {user["id"]: user for user in includes.get("users", [])}
    media = {
        media_obj["media_key"]: media_obj for media_obj in includes.get("media", [])
    }

    # Build a formatted string of tweet details
    res_str = ""
    for tweet in tweets:
        author = (
            users[tweet.author_id].username if tweet.author_id in users else "Unknown"
        )
        res_str += f"Tweet ID: {tweet.id}, Author: {author}\n"
        res_str += f"Text: {tweet.text}\n"
        res_str += f"Posted At: {tweet.created_at}\n"

        # Check for media and add URLs
        if "attachments" in tweet.data and "media_keys" in tweet.data["attachments"]:
            media_keys = tweet.data["attachments"]["media_keys"]
            for key in media_keys:
                if key in media and media[key]["type"] == "photo":
                    res_str += f"Image URL: {media[key]['url']}\n"
        res_str += "-" * 40 + "\n"

    return res_str


def get_user_info(username: int):
    """
    Retrieve information about a Twitter user based on their username or user ID.
    Args:
        username (Union[str, int, None]): The user's identifier.
    Returns:
        tweepy.User: An object containing the user's details.
    """
    import tweepy
    from memeai.twitter.config import settings

    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    if isinstance(username, str):
        user = client.get_user(
            username=username,
            user_fields=["id", "name", "username", "description", "public_metrics"],
        )
    elif isinstance(username, int):
        user = client.get_user(
            id=username,
            user_fields=["id", "name", "username", "description", "public_metrics"],
        )
    return user


def tweet(message: str):
    """
    Post a tweet to the authenticated user's Twitter account.

    Args:
        message (str): The content of the tweet, which must adhere to Twitter's character limit.

    Returns:
        tweepy.Response: The API response containing details of the posted tweet, including its ID.

    Example:
        >>> response = tweet("Hello, world!")
        >>> print(f"Tweet URL: https://twitter.com/user/status/{response.data['id']}")

    Raises:
        tweepy.TweepyException: If the API call fails due to invalid credentials or other issues.
    """
    # from memeai.twitter.config import settings
    import tweepy
    import emoji
    from memeai.twitter.config import settings

    message = emoji.replace_emoji(message, replace='')

    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )
    tweet = client.create_tweet(text=message)
    print(f"https://twitter.com/user/status/{tweet.data['id']}")
    return tweet


def get_home_timeline(max_results: int = 5) -> str:
    """
    Retrieve tweets from the home timeline with expanded information.

    Args:
        max_results (int, optional): The maximum number of tweets to retrieve. Defaults to 5.

    Returns:
        str: A formatted string representing tweets with user information, or a message if no tweets are found.

    Raises:
        ValueError: If no tweets are returned by the API.
        tweepy.TweepyException: If the API call fails.
    """
    import tweepy
    from memeai.twitter.config import settings

    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        response = client.get_home_timeline(
            max_results=max_results,
            tweet_fields=["created_at", "public_metrics"],
            expansions=["author_id"],
            user_fields=["username"],
            user_auth=True,
        )
        if not response.data:
            raise ValueError("No tweets found in the timeline.")

        tweets = []
        for tweet in response.data:
            tweets.append(f"Tweet ID: {tweet.id}\nContent: {tweet.text}\n{'-' * 20}")

        return "\n".join(tweets)

    except tweepy.TweepyException as e:
        print(f"Error fetching timeline: {e}")
        return "An error occurred while fetching the timeline."

    except ValueError as ve:
        print(f"Validation error: {ve}")
        return "No tweets found in the timeline."


def put_like(tweet_id: int) -> str:
    """
    Like a tweet by its ID.

    Args:
        tweet_id (int): The ID of the tweet to like.

    Returns:
        str: A success message if the tweet is liked, or an error message if the operation fails.

    Raises:
        tweepy.TweepyException: If the API call fails.
    """
    import tweepy
    from memeai.twitter.config import settings

    # Initialize Tweepy client
    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        # Perform the like action
        response = client.like(tweet_id)

        # Check for successful operation
        if response.data:
            return f"Successfully liked tweet with ID: {tweet_id}"
        else:
            return "Failed to like the tweet. No response data returned."

    except tweepy.TweepyException as e:
        print(f"Error liking tweet: {e}")
        return "An error occurred while liking the tweet."


def retweet(tweet_id: int) -> str:
    """
    Retweet a tweet by its ID.

    Args:
        tweet_id (int): The ID of the tweet to retweet.

    Returns:
        str: A success message if the tweet is retweeted, or an error message if the operation fails.

    Raises:
        tweepy.TweepyException: If the API call fails.
        TypeError: If the access token isn't set.
    """
    import tweepy
    from memeai.twitter.config import settings

    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        # Perform the retweet action
        response = client.retweet(tweet_id, user_auth=True)

        # Check for successful operation
        if response.data:
            return f"Successfully retweeted tweet with ID: {tweet_id}"
        else:
            return "Failed to retweet the tweet. No response data returned."

    except tweepy.TweepyException as e:
        print(f"Error retweeting: {e}")
        return "An error occurred while retweeting the tweet."

    except TypeError as te:
        print(f"Type error: {te}")
        return "An error occurred due to an issue with the access token."


def unretweet(tweet_id: int) -> str:
    """
    Remove the Retweet of a tweet by its ID.

    Args:
        tweet_id (int): The ID of the tweet to unretweet.

    Returns:
        str: A success message if the Retweet is removed, or an error message if the operation fails.

    Raises:
        tweepy.TweepyException: If the API call fails.
        TypeError: If the access token isn't set.
    """
    import tweepy
    from memeai.twitter.config import settings

    # Initialize Tweepy client
    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        # Perform the unretweet action
        response = client.unretweet(tweet_id, user_auth=True)

        # Check for successful operation
        if response.data:
            return f"Successfully removed Retweet for tweet with ID: {tweet_id}"
        else:
            return "Failed to unretweet the tweet. No response data returned."

    except tweepy.TweepyException as e:
        print(f"Error unretweeting: {e}")
        return "An error occurred while removing the Retweet."

    except TypeError as te:
        print(f"Type error: {te}")
        return "An error occurred due to an issue with the access token."


def respond_to_mentions(tweet_id: int, response_text: str) -> str:
    """
    Fetch mentions directed at the user and reply to those in the thread of a specific tweet.

    Args:
        tweet_id (int): The ID of the tweet to filter mentions from.
        response_text (str): The text of the response to post to each mention.

    Returns:
        str: A summary message about the operation's success or failure.

    Raises:
        tweepy.TweepyException: If the API call fails.
        TypeError: If the access token isn't set.
    """
    import tweepy
    import emoji
    from memeai.twitter.config import settings

    response_text = emoji.replace_emoji(response_text, replace='')

    # Initialize Tweepy client
    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        # Fetch recent mentions for the authenticated user
        mentions = client.get_users_mentions(
            user_id="self",
            tweet_fields=["conversation_id", "author_id", "text"],
            expansions=["author_id"],
            max_results=100,
        )

        if not mentions.data:
            return f"No mentions found for the authenticated user."

        success_count = 0
        failure_count = 0

        # Filter mentions by conversation ID and respond to them
        for mention in mentions.data:
            if str(mention.conversation_id) == str(tweet_id):  # Match thread ID
                try:
                    client.create_tweet(
                        text=response_text, in_reply_to_tweet_id=mention.id
                    )
                    success_count += 1
                except tweepy.TweepyException as e:
                    print(f"Failed to respond to mention {mention.id}: {e}")
                    failure_count += 1

        if success_count == 0:
            return f"No mentions found in the thread of tweet ID: {tweet_id}"

        return f"Successfully responded to {success_count} mentions. Failed to respond to {failure_count}."

    except tweepy.TweepyException as e:
        print(f"Error fetching mentions: {e}")
        return "An error occurred while fetching mentions."

    except TypeError as te:
        print(f"Type error: {te}")
        return "An error occurred due to an issue with the access token."


def reply_to_tweet(tweet_id: int, reply_text: str) -> str:
    """
    Post a reply to a specific tweet.

    Args:
        tweet_id (int): The ID of the tweet to reply to.
        reply_text (str): The text of the reply.

    Returns:
        str: A success message with the tweet ID of the reply or an error message if it fails.

    Raises:
        tweepy.TweepyException: If the API call fails.
        TypeError: If the access token isn't set.
    """
    import tweepy
    import emoji
    from memeai.twitter.config import settings

    reply_text = emoji.replace_emoji(reply_text, replace='')
    # Initialize Tweepy client
    client = tweepy.Client(
        consumer_key=settings.API_SECRET,
        consumer_secret=settings.API_SECRET,
        access_token=settings.ACCESS_TOKEN,
        access_token_secret=settings.ACCESS_TOKEN_SECRET,
        bearer_token=settings.BEARER_TOKEN,
    )

    try:
        # Post the reply
        response = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)

        # Check if the reply was successfully posted
        if response.data:
            return f"Successfully replied to tweet with ID: {tweet_id}. Reply ID: {response.data['id']}"
        else:
            return "Failed to post the reply. No response data returned."

    except tweepy.TweepyException as e:
        print(f"Error posting reply: {e}")
        return f"An error occurred while posting the reply: {str(e)}"

    except TypeError as te:
        print(f"Type error: {te}")
        return f"An error occurred due to an issue with the access token: {str(te)}"
