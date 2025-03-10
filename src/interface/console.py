# src/interface/console.py
import logging


class ConsoleInterface:
    """Simple text-based console interface for the content creation agent."""

    def __init__(self, interaction_engine):
        """Initialize with an interaction engine."""
        self.interaction = interaction_engine
        self.logger = logging.getLogger(__name__)
        self.session_active = False

    def start(self):
        """Start the console interface."""
        print("Welcome to the Content Creation AI Agent!")
        print("Type 'exit' to quit at any time.")

        while True:
            if not self.session_active:
                self._setup_session()

            user_input = input("\nYou: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            response = self.interaction.process_user_input(user_input)
            print(f"\nAgent: {response}")

    def _setup_session(self):
        """Set up a new content creation session."""
        print("\nLet's start a new content creation session.")

        content_types = ["blog_post", "twitter_thread", "linkedin_post"]
        print("What type of content would you like to create?")
        for i, content_type in enumerate(content_types, 1):
            print(f"{i}. {content_type}")

        while True:
            try:
                choice = int(input("Enter the number of your choice: "))
                if 1 <= choice <= len(content_types):
                    content_type = content_types[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")

        topic = input("What's the main topic of your content? ")

        welcome_message = self.interaction.start_session(content_type, topic)
        print(f"\nAgent: {welcome_message}")

        self.session_active = True
