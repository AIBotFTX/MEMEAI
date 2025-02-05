from letta import ChatMemory, EmbeddingConfig, LLMConfig
from typing import List, Dict
from pydantic import BaseModel
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
# from memeai.agents.tool_creation import create_angent
import json


def create_agent(funcs: List[str], system_prompts: str, metadata: dict) -> str:
    """
    Creates an AI agent using the MemeAI Twitter client.

    This function registers specified functions as tools, configures the agent's memory,
    and initializes the agent with the given system prompts and metadata.

    Args:
        funcs (list of str): List of function names to be registered as tools if they exist in GLOBAL_FUNCTIONS.
        system_prompts (str): System prompt configuration for the agent.
        metadata (dict): Dictionary containing agent metadata, including:
            - "name" (str): The name of the agent.
            - "persona" (str): The persona description for the agent's memory.

    Returns:
        str: The unique ID of the created agent.
    """
    from memeai.agents.global_functions import GLOBAL_FUNCTIONS
    from letta import ChatMemory, EmbeddingConfig, LLMConfig
    from letta import create_client
    functions = []
    for f in funcs:
        if f in GLOBAL_FUNCTIONS:
            functions.append(GLOBAL_FUNCTIONS[f])
    tools = []
    for func in functions:
        tool = client.create_or_update_tool(func)
        tools.append(tool.id)

    agent_state = create_client(
        name=metadata["name"],
        memory=ChatMemory(human="", persona=metadata["persona"]),
        llm_config=LLMConfig(
            model="claude-3-opus-20240229",
            model_endpoint_type="anthropic",
            model_endpoint="https://api.anthropic.com/v1",
            context_window=10000,
        ),
        embedding_config=EmbeddingConfig.default_config(model_name="letta"),
        system=system_prompts,
        tool_ids=tools,
        include_base_tools=True,
    )
    return agent_state.id



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
        create_agent,
    ]
    tools = []
    for func in functions:
        tool = client.create_or_update_tool(func)
        tools.append(tool.id)

    agent_state = client.create_agent(
        name="AGI",
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
