# from memeai.agents.global_functions import GLOBAL_FUNCTIONS


# def create_agent(funcs, system_prompts, metadata):
#     """
#     Creates an AI agent using the MemeAI Twitter client.

#     This function registers specified functions as tools, configures the agent's memory,
#     and initializes the agent with the given system prompts and metadata.

#     Args:
#         funcs (list of str): List of function names to be registered as tools if they exist in GLOBAL_FUNCTIONS.
#         system_prompts (str): System prompt configuration for the agent.
#         metadata (dict): Dictionary containing agent metadata, including:
#             - "name" (str): The name of the agent.
#             - "persona" (str): The persona description for the agent's memory.

#     Returns:
#         str: The unique ID of the created agent.
#     """
#     from memeai.twitter.client import client
#     from letta import ChatMemory, EmbeddingConfig, LLMConfig

#     functions = []
#     for f in funcs:
#         if f in GLOBAL_FUNCTIONS:
#             functions.append(GLOBAL_FUNCTIONS[f])
#     tools = []
#     for func in functions:
#         tool = client.create_or_update_tool(func)
#         tools.append(tool.id)

#     agent_state = client.create_agent(
#         name=metadata["name"],
#         memory=ChatMemory(human="", persona=metadata["persona"]),
#         llm_config=LLMConfig(
#             model="claude-3-opus-20240229",
#             model_endpoint_type="anthropic",
#             model_endpoint="https://api.anthropic.com/v1",
#             context_window=10000,
#         ),
#         embedding_config=EmbeddingConfig.default_config(model_name="letta"),
#         system=system_prompts,
#         tool_ids=tools,
#         include_base_tools=True,
#     )
#     return agent_state.id
