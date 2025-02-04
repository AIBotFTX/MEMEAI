from letta import ChatMemory, EmbeddingConfig, LLMConfig
from memeai.twitter.client import client
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
from memeai.agents.tool_creation import create_angent
import json


def tweet_memory(text, date):
    return f"SBF post: On {date}, you posted {text.split(' ')}."


with open("/app/memeai/memory_.json", "r") as file:
    memories = json.load(file)

with open("/app/memeai/sbf.txt", "r") as file:
    persona = file.read()

with open("/app/memeai/sbf_memory.txt", "r") as file:
    system = file.read()


def init_agent():
    functions = [
        search_tweets_with_media,
        get_user_info,
        tweet,
        get_home_timeline,
        put_like,
        retweet,
        unretweet,
        reply_to_tweet,
        respond_to_mentions,
        create_angent,
    ]
    tools = []
    for func in functions:
        tool = client.create_or_update_tool(func)
        tools.append(tool.id)

    agent_state = client.create_agent(
        name="SBF_AGI",
        memory=ChatMemory(human="", persona=persona),
        llm_config=LLMConfig(
            model="claude-3-opus-20240229",
            model_endpoint_type="anthropic",
            model_endpoint="https://api.anthropic.com/v1",
            context_window=10000,
        ),
        embedding_config=EmbeddingConfig.default_config(model_name="letta"),
        system=system,
        tool_ids=tools,
        include_base_tools=True,
    )
    for memory in memories["data"]:
        client.insert_archival_memory(
            agent_state.id, tweet_memory(memory["text"], memory["created_at"])
        )

    print(f"Created agent with name {agent_state.name} and unique ID {agent_state.id}")
    return agent_state.id
