from memeai.agents.global_functions import GLOBAL_FUNCTIONS


def create_angent(funcs, system_prompts, metadata):
    from memeai.twitter.client import client
    from letta import ChatMemory, EmbeddingConfig, LLMConfig

    functions = []
    for f in funcs:
        if f in GLOBAL_FUNCTIONS:
            functions.append(GLOBAL_FUNCTIONS[f])
    tools = []
    for func in functions:
        tool = client.create_or_update_tool(func)
        tools.append(tool.id)

    agent_state = client.create_agent(
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
