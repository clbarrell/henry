# tests/test_interaction.py
import pytest
from unittest.mock import MagicMock
from src.engine.interaction import InteractionEngine
from src.engine.phase import ContentPhase, PhaseController


class TestInteractionEngine:
    """Tests for the InteractionEngine class."""

    @pytest.fixture
    def setup(self):
        """Set up an interaction engine with mocked dependencies."""
        memory = MagicMock()
        memory.get_current_phase.return_value = "Context Gathering"
        memory.add_user_input.return_value = "input-id"
        memory.add_question.return_value = "question-id"

        controller = MagicMock()
        controller.get_current_phase.return_value = ContentPhase.CONTEXT_GATHERING
        controller.get_phase_prompts.return_value = ["Test question?"]
        controller.reverse_phase_map = {
            ContentPhase.CONTEXT_GATHERING: "Context Gathering"
        }

        engine = InteractionEngine(memory, controller)

        return memory, controller, engine

    def test_start_session(self, setup):
        """Test starting a new session."""
        memory, controller, engine = setup

        welcome_message = engine.start_session("blog_post", "Test Topic")

        assert "Welcome" in welcome_message
        assert "Test Topic" in welcome_message
        memory.start_new_session.assert_called_once_with("blog_post", "Test Topic")

    def test_process_help_command(self, setup):
        """Test processing the help command."""
        memory, controller, engine = setup

        response = engine.process_user_input("/help")

        assert "Available commands" in response
        memory.add_user_input.assert_called_once_with("/help", None)
