# src/interface/console.py
import logging
from rich.console import Console
from rich.prompt import Prompt
import questionary
from questionary import Style as QuestionaryStyle


class ConsoleInterface:
    """Rich text-based console interface for the content creation agent."""

    def __init__(self, interaction_engine):
        """Initialize with an interaction engine."""
        self.interaction = interaction_engine
        self.logger = logging.getLogger(__name__)
        self.session_active = False
        self.console = Console()

        # Define custom styles for questionary
        self.custom_style = QuestionaryStyle(
            [
                ("qmark", "fg:cyan bold"),
                ("question", "fg:white bold"),
                ("answer", "fg:green bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan bold"),
                ("selected", "fg:green bold"),
                ("separator", "fg:cyan"),
                ("instruction", "fg:white"),
                ("text", "fg:white"),
                ("disabled", "fg:gray italic"),
            ]
        )

    def start(self):
        """Start the console interface."""
        self.console.print("[bold]Welcome to the Content Creation AI Agent![/bold]")
        self.console.print("Type [italic]'exit'[/italic] to quit at any time.")

        while True:
            if not self.session_active:
                self._setup_session()

            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if user_input.lower() == "exit":
                self.console.print("[bold]Goodbye![/bold]")
                break

            response = self.interaction.process_user_input(user_input)
            self.console.print(f"\n[bold green]Agent[/bold green]: {response}")

    def _setup_session(self):
        """Set up a new content creation session."""
        self.console.print("\n[bold]Let's start a new content creation session.[/bold]")

        content_types = ["blog_post", "twitter_thread", "linkedin_post"]

        # Use questionary for content type selection
        content_type = questionary.select(
            "What type of content would you like to create?",
            choices=content_types,
            style=self.custom_style,
        ).ask()

        if not content_type:  # Handle case where user cancels
            content_type = "blog_post"  # Default

        topic = Prompt.ask(
            "[bold cyan]What's the main topic of your content?[/bold cyan]"
        )

        welcome_message = self.interaction.start_session(content_type, topic)
        self.console.print(f"\n[bold green]Agent[/bold green]: {welcome_message}")

        self.session_active = True
