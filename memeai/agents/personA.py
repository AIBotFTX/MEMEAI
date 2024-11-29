from memeai.agents.base_persona import BasePersona
from typing import Any, List, Dict, Optional
from langchain_community.chat_models import ChatAnthropic
from langchain.experimental.generative_agents import GenerativeAgent
import logging

logging.basicConfig(level=logging.ERROR)


class Person(BasePersona):
    def __init__(
        self,
        name: str,
        model: Optional[ChatAnthropic],
        description: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize a Person with a given name, language model, description, and optional interaction history.
        """
        super().__init__(model=model, description=description, history=history or [])
        self.name = name
        self.personality = None

    @classmethod
    async def create(
        cls, name: str, model: ChatAnthropic, description: Dict[str, Any],
        **kwargs
    ) -> "Person":
        """
        Asynchronous factory method to create a Person with a personality.
        """
        instance = cls(name, model, description, history=kwargs.get("history", []))
        await instance.set_personality(**kwargs)
        return instance

    async def set_personality(
        self, name: str, age: int, traits: List[str], status: str, retriever,
        memory
    ) -> None:
        """
        Asynchronously sets the personality for this Person using
        GenerativeAgent.
        """
        self.personality = GenerativeAgent(
            name=name,
            age=age,
            traits=traits,
            status=status,
            memory_retriever=retriever,
            llm=self.model,
            memory=memory,
        )
        await self.update_history()
        summary = self.personality.get_summary(force_refresh=True)
        print(f"Personality set for {self.name}. Summary: {summary}")

    async def generate_prompt(self, message: str) -> str:
        """
        Generate a response to a given message using the person's personality.
        """
        if self.personality is None:
            raise ValueError("Personality not set. Please initialize it first.")
        return self.personality.generate_dialogue_response(message)[1]

    async def update_history(self) -> None:
        """
        Update the personality's memory with this Person's historical
         observations.
        """
        if not self.history:
            return
        for observation in self.history:
            self.personality.add_memory(observation)

    def reset_history(self) -> None:
        """
        Reset the interaction history.
        """
        self.history = []
