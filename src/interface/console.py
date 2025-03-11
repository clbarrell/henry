# src/interface/console.py
import logging
from rich.console import Console
from rich.prompt import Prompt
import questionary
from questionary import Style as QuestionaryStyle
import signal
from datetime import datetime


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

        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self._handle_interrupt)

        try:
            while True:
                if not self.session_active:
                    self._choose_session()

                try:
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                    if user_input.lower() == "exit":
                        self.console.print("[bold]Goodbye![/bold]")
                        break

                    response = self.interaction.process_user_input(user_input)
                    self.console.print(f"\n[bold green]Agent[/bold green]: {response}")
                except KeyboardInterrupt:
                    # Handle Ctrl+C during input
                    self._handle_interrupt(None, None)
        except Exception as e:
            self.logger.error(f"Error in console interface: {e}", exc_info=True)
            self.console.print(f"[bold red]An error occurred: {e}[/bold red]")
        finally:
            # Clean up
            self.console.print("[bold]Exiting...[/bold]")

    def _handle_interrupt(self, sig, frame):
        """Handle keyboard interruption (Ctrl+C)."""
        self.console.print("\n\n[bold yellow]Session interrupted.[/bold yellow]")

        try:
            # Ask if user wants to save and exit
            if questionary.confirm(
                "Do you want to save your progress and exit?",
                default=True,
                style=self.custom_style,
            ).ask():
                self.console.print(
                    "[bold green]Progress saved. You can resume this session later.[/bold green]"
                )

            self.console.print("[bold]Goodbye![/bold]")
            # Exit gracefully
            exit(0)
        except Exception as e:
            self.logger.error(f"Error handling interruption: {e}", exc_info=True)
            exit(1)

    def _choose_session(self):
        """Choose between starting a new session or resuming an existing one."""
        self.console.print("\n[bold]Choose an option:[/bold]")

        # Get available sessions
        sessions = self.interaction.memory.list_sessions()

        # Create choices
        choices = ["Start a new session"]

        # Add existing sessions if available
        session_map = {}
        if sessions:
            for session in sessions:
                # Format the date
                created_date = session["created"].strftime("%Y-%m-%d %H:%M")
                choice_text = f"{session['topic']} ({session['type']}) - {created_date}"
                choices.append(choice_text)
                session_map[choice_text] = session["id"]

        # Ask user to choose
        choice = questionary.select(
            "What would you like to do?", choices=choices, style=self.custom_style
        ).ask()

        if choice == "Start a new session":
            self._setup_session()
        else:
            # Resume the selected session
            session_id = session_map[choice]
            welcome_message = self.interaction.resume_session(session_id)
            if welcome_message:
                self.console.print(
                    f"\n[bold green]Agent[/bold green]: {welcome_message}"
                )
                self.session_active = True
            else:
                self.console.print(
                    "[bold red]Failed to resume session. Starting a new one.[/bold red]"
                )
                self._setup_session()

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
