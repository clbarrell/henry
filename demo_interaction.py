#!/usr/bin/env python
# demo_interaction.py
"""
Demo script to showcase the enhanced interaction engine with Rich and Questionary.
"""

import logging
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.interaction import InteractionEngine
from src.engine.phase import PhaseController, ContentPhase
from src.memory.graph_db import MemoryManager
from rich.console import Console

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class MockMemoryManager(MemoryManager):
    """Mock memory manager for demo purposes."""

    def __init__(self):
        """Initialize with mock Neo4j driver."""
        self.logger = logging.getLogger(__name__)
        self.session_id = "mock-session-id"
        self.current_phase_id = "mock-phase-id"

        # Mock the Neo4j driver
        self.driver = MagicMock()

        # Mock session context manager
        mock_session = MagicMock()
        self.driver.session.return_value.__enter__.return_value = mock_session

        # Mock query results
        mock_result = MagicMock()
        mock_record = {"content_id": self.session_id, "phase_id": self.current_phase_id}
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result

    def get_current_phase(self):
        """Get the current phase name."""
        return "Context Gathering"

    def add_user_input(self, text, response_to=None):
        """Mock storing user input."""
        return "mock-input-id"

    def add_question(self, text, intent=None):
        """Mock storing a question."""
        return "mock-question-id"

    def start_new_session(self, content_type, topic):
        """Mock starting a new session."""
        return self.session_id

    def transition_phase(self, new_phase_name):
        """Mock transitioning to a new phase."""
        return True


def main():
    """Run a demo of the interaction engine with enhanced UI."""
    console = Console()

    # Print a welcome header
    console.print(
        "\n[bold magenta]===== Content Creation Assistant Demo =====\n[/bold magenta]"
    )

    # Initialize components
    memory_manager = MockMemoryManager()
    phase_controller = PhaseController(memory_manager)
    interaction_engine = InteractionEngine(memory_manager, phase_controller)

    # Start a new session using questionary for input
    content_types = ["Blog Post", "Article", "Essay", "Report", "Social Media Post"]
    content_type = interaction_engine.get_user_choice(
        "What type of content would you like to create?",
        choices=content_types,
        default="Blog Post",
    )

    topic = interaction_engine.get_user_input(
        "What topic would you like to write about?"
    )

    # Start the session
    welcome_message = interaction_engine.start_session(content_type, topic)
    interaction_engine.display_message(welcome_message, style="info")

    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = interaction_engine.get_user_input()

            # Process user input
            response = interaction_engine.process_user_input(user_input)

            # Display the response
            if "error" in response.lower():
                interaction_engine.display_message(response, style="error")
            else:
                interaction_engine.display_message(response, style="success")

            # Handle special interactive menu command
            if user_input.lower() == "/menu":
                options = [
                    "Add a new section",
                    "Modify existing content",
                    "Change writing style",
                    "Add references",
                    "Include examples",
                ]
                selected_options = interaction_engine.get_user_checkbox(
                    "Select options for your content:", choices=options
                )

                if selected_options:
                    result = f"You selected: {', '.join(selected_options)}"
                    interaction_engine.display_message(result, style="info")
                else:
                    interaction_engine.display_message(
                        "No options selected", style="warning"
                    )

            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit", "/exit", "/quit"]:
                if interaction_engine.get_user_confirmation(
                    "Are you sure you want to exit?"
                ):
                    break

        except KeyboardInterrupt:
            console.print("\n[bold red]Exiting...[/bold red]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            logging.error(f"Error in interaction loop: {e}", exc_info=True)

    # Show a goodbye message
    console.print(
        "\n[bold blue]Thank you for using the Content Creation Assistant![/bold blue]"
    )


if __name__ == "__main__":
    main()
