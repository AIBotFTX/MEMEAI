from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from langchain_core.language_models.chat_models import BaseChatModel


class BasePersona(ABC):
    def __init__(
        self,
        name: str = "BasePersona",
        model: Optional[BaseChatModel] = None,
        description: Dict[str, Any] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the agent with a name, description, and optional history.

        :param name: Name of the agent.
        :param model: The chat model instance.
        :param description: Brief description of the agent's persona.
        :param history: List of interaction history.
        """
        self.name = name
        self.model = model
        self.description = description if description else {}
        self.history = history if history else []

    @abstractmethod
    def name(self) -> str:
        return self.name

    @abstractmethod
    async def set_personality(self, **kwargs) -> str:
        """
       This method sets personality for LLM
       by comining desciption and history.

        """
        raise NotImplementedError("The set_personality is not implemented.")

    @abstractmethod
    async def generate_prompt(self) -> str:
        """
        Generate a personalized prompt or message based on the agent's persona and history.

        :return: Generated prompt.
        """
        raise NotImplementedError("The generate_prompt is not implemented.")

    @abstractmethod
    async def update_history(self, interaction: Dict[str, Any]) -> None:
        """
        Update the agent's interaction history.

        :param interaction: Dictionary containing interaction details.
        """
        raise NotImplementedError("The update_personality is not implemented.")

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset the agent's state and history.
        """
        raise NotImplementedError("The reset is not implemented.")
