import pytest
from typing import Any, Dict
from unittest.mock import Mock
from memeai.agents.base_persona import BasePersona


class MockPersona(BasePersona):
    def name(self) -> str:
        return "MockPersona"

    async def set_personality(self) -> str:
        return "Personality set"

    async def generate_prompt(self) -> str:
        return "Generated prompt"

    async def update_history(self, interaction: Dict[str, Any]) -> None:
        self.history.append(interaction)

    async def reset(self) -> None:
        self.history = []


@pytest.mark.asyncio
class TestMockPersona:
    @pytest.fixture
    def mock_persona(self):
        model = Mock()  # Replace with a mock model
        description = {"description": "test"}
        return MockPersona(model, description)

    async def test_name(self, mock_persona):
        assert mock_persona.name() == "MockPersona"

    async def test_set_personality(self, mock_persona):
        result = await mock_persona.set_personality()
        assert result == "Personality set"

    async def test_generate_prompt(self, mock_persona):
        result = await mock_persona.generate_prompt()
        assert result == "Generated prompt"

    async def test_update_history(self, mock_persona):
        interaction = {"user": "test", "response": "response"}
        await mock_persona.update_history(interaction)
        assert interaction in mock_persona.history

    async def test_reset(self, mock_persona):
        await mock_persona.reset()
        assert mock_persona.history == []
