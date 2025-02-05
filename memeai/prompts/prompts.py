from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str


class PromptRequest(BaseModel):
    prompts: list[Prompt]
