# src/engine/interaction.py
import logging
import random
import uuid
from src.engine.phase import ContentPhase
from src.llm import LLMClient, AgentState, PromptManager

# Import Rich and Questionary libraries
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
import questionary
from questionary import Style as QuestionaryStyle


class InteractionEngine:
    """Manages the conversation flow and question generation."""

    def __init__(
        self, memory_manager, phase_controller, llm_client=None, prompt_manager=None
    ):
        """Initialize with memory manager, phase controller, and optional LLM components."""
        self.memory = memory_manager
        self.phase_controller = phase_controller
        self.logger = logging.getLogger(__name__)
        self.last_question_id = None

        # Initialize LLM components if provided, otherwise use default behavior
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.agent_state = AgentState() if llm_client else None
        self.use_llm = llm_client is not None and prompt_manager is not None

        # Create a session ID for the agent state
        self.session_id = str(uuid.uuid4())
        if self.agent_state:
            self.agent_state.session_id = self.session_id

        # Initialize Rich console
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

    def process_user_input(self, text):
        """Process user input and determine next agent action."""
        # Store the user input
        input_id = self.memory.add_user_input(text, self.last_question_id)
        self.logger.info(f"Stored user input: {text[:50]}...")

        # Add to agent state if using LLM
        if self.use_llm:
            self.agent_state.add_message("user", text)

        # Check for commands
        if text.startswith("/"):
            return self._handle_command(text)

        # Use LLM for analysis if available
        if self.use_llm:
            return self._process_with_llm(text)
        else:
            # Fall back to simple keyword checking
            return self._process_with_keywords(text)

    def _process_with_llm(self, text):
        """Process user input using LLM for analysis."""
        try:
            # Get conversation context from agent state
            conversation_context = self.agent_state.get_recent_context()

            # Get current phase and system prompt
            current_phase = self.phase_controller.get_current_phase()
            phase_name = self.phase_controller.reverse_phase_map[current_phase]
            system_prompt = self.prompt_manager.get_prompt(
                f"phases.{phase_name.lower().replace(' ', '_')}"
            )

            # Analyze input with Claude
            analysis = self.llm_client.analyze_input(
                conversation_context, system_prompt, phase_name
            )

            # Update agent state with analysis
            self.agent_state.set_analysis_result(analysis)

            # Check if we should transition to the next phase
            if analysis.get("should_transition", False):
                transition_message = analysis.get(
                    "transition_message",
                    f"Great! We've gathered enough information for the {phase_name} phase. Let's move on to the next phase.",
                )
                self.phase_controller.transition_to_next_phase()
                next_question = self.get_next_question()

                # Add assistant message to agent state
                self.agent_state.add_message(
                    "assistant", transition_message + "\n\n" + next_question
                )

                return transition_message + "\n\n" + next_question

            # Generate next question
            next_question = self.get_next_question()

            # Add assistant message to agent state
            self.agent_state.add_message("assistant", next_question)

            return next_question
        except Exception as e:
            self.logger.error(f"Error in LLM processing: {e}", exc_info=True)
            # Fall back to keyword processing if LLM fails
            return self._process_with_keywords(text)

    def _process_with_keywords(self, text):
        """Process user input using simple keyword checking."""
        # Check if we can transition to the next phase
        if self._should_transition_phase(text):
            current_phase = self.phase_controller.get_current_phase()
            next_phase_msg = f"Great! We've gathered enough information for the {current_phase.name.lower()} phase. "
            next_phase_msg += "Let's move on to the next phase."
            self.phase_controller.transition_to_next_phase()
            return next_phase_msg + "\n\n" + self.get_next_question()

        # Generate next question
        return self.get_next_question()

    def _should_transition_phase(self, text):
        """Determine if we should transition to the next phase based on user input."""
        # In a real implementation, this would use more sophisticated analysis
        current_phase = self.phase_controller.get_current_phase()

        # Simple keyword checking for demonstration purposes
        if current_phase == ContentPhase.CONTEXT_GATHERING:
            keywords = ["next", "structure", "outline", "move on", "enough context"]
            return any(keyword in text.lower() for keyword in keywords)

        elif current_phase == ContentPhase.STRUCTURE_DEVELOPMENT:
            keywords = ["next", "content", "details", "expand", "flesh out", "move on"]
            return any(keyword in text.lower() for keyword in keywords)

        elif current_phase == ContentPhase.CONTENT_DEVELOPMENT:
            keywords = ["next", "refine", "review", "finalize", "polish", "revise"]
            return any(keyword in text.lower() for keyword in keywords)

        return False

    def _handle_command(self, command):
        """Handle special commands."""
        command = command.strip().lower()

        if command == "/help":
            help_text = (
                "Available commands:\n"
                "/help - Show this help message\n"
                "/status - Show the current phase and progress\n"
                "/export - Export the content\n"
                "/next - Move to the next phase\n"
                "/menu - Show interactive menu options"
            )
            # Return rich formatted help text
            return self._format_system_message(help_text, "Help Commands")

        elif command == "/status":
            current_phase = self.phase_controller.get_current_phase()
            phase_name = self.phase_controller.reverse_phase_map[current_phase]

            # Add confidence information if using LLM
            if self.use_llm:
                confidence = self.agent_state.get_phase_confidence(phase_name.lower())
                confidence_str = f" (Confidence: {confidence:.0%})"
                status_text = f"Current phase: {phase_name}{confidence_str}"
            else:
                status_text = f"Current phase: {phase_name}"

            return self._format_system_message(status_text, "Status")

        elif command == "/export":
            # Simplified export functionality
            export_text = "Content export would happen here (not implemented in MVP)"
            return self._format_system_message(export_text, "Export")

        elif command == "/menu":
            # Interactive menu using questionary checkbox
            options = [
                "Add a new section",
                "Modify existing content",
                "Change writing style",
                "Add references",
                "Include examples",
            ]

            # This will be handled in the demo script
            return self._format_system_message(
                "Please select options from the interactive menu that will appear.",
                "Interactive Menu",
            )

        elif command == "/next":
            if self.phase_controller.transition_to_next_phase():
                current_phase = self.phase_controller.get_current_phase()
                phase_name = self.phase_controller.reverse_phase_map[current_phase]
                next_text = (
                    f"Moving to {phase_name} phase.\n\n{self.get_next_question()}"
                )
                return self._format_system_message(next_text, "Phase Transition")
            else:
                error_text = "Cannot transition to next phase. You may already be in the final phase."
                return self._format_system_message(error_text, "Error")

        else:
            error_text = (
                f"Unknown command: {command}. Type /help for available commands."
            )
            return self._format_system_message(error_text, "Error")

    def _format_system_message(self, text, title=None):
        """Format system messages with Rich styling."""
        if title:
            return f"[bold cyan]{title}[/bold cyan]\n[white]{text}[/white]"
        return f"[cyan]{text}[/cyan]"

    def get_next_question(self):
        """Generate the next question based on the current phase and context."""
        current_phase = self.phase_controller.get_current_phase()
        phase_name = self.phase_controller.reverse_phase_map[current_phase]

        # Use LLM for question generation if available
        if self.use_llm:
            try:
                conversation_context = self.agent_state.get_recent_context()
                system_prompt = self.prompt_manager.get_prompt(
                    f"phases.{phase_name.lower().replace(' ', '_')}"
                )

                question = self.llm_client.generate_question(
                    conversation_context, system_prompt, phase_name
                )
            except Exception as e:
                self.logger.error(
                    f"Error generating question with LLM: {e}", exc_info=True
                )
                # Fall back to random selection if LLM fails
                phase_prompts = self.phase_controller.get_phase_prompts()
                question = random.choice(phase_prompts)
        else:
            # Use random selection from predefined prompts
            phase_prompts = self.phase_controller.get_phase_prompts()
            question = random.choice(phase_prompts)

        # Store the question in memory
        question_id = self.memory.add_question(question, intent=phase_name)
        self.last_question_id = question_id

        # Format the question with Rich styling
        return f"[bold green]Question:[/bold green] [white]{question}[/white]"

    def get_user_input(self, prompt=None):
        """Get user input with Rich styling."""
        if prompt is None:
            prompt = "Your response"

        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]")

    def get_user_confirmation(self, question):
        """Get user confirmation with Rich styling."""
        return Confirm.ask(f"[bold cyan]{question}[/bold cyan]")

    def get_user_choice(self, question, choices, default=None):
        """Get user choice from a list of options using questionary."""
        return questionary.select(
            question, choices=choices, default=default, style=self.custom_style
        ).ask()

    def get_user_checkbox(self, question, choices):
        """Get multiple user choices using questionary checkboxes."""
        return questionary.checkbox(
            question, choices=choices, style=self.custom_style
        ).ask()

    def start_session(self, content_type, topic):
        """Start a new content creation session."""
        self.memory.start_new_session(content_type, topic)

        # Reset agent state if using LLM
        if self.use_llm:
            self.agent_state.reset()
            self.agent_state.session_id = self.session_id
            self.agent_state.current_topic = topic
            self.agent_state.content_type = content_type

        welcome_message = (
            f"Welcome to your {content_type} creation session about '[bold yellow]{topic}[/bold yellow]'!\n\n"
            f"We'll start by gathering some context about what you want to write. "
            f"I'll ask you questions to help organize your thoughts, and then we'll "
            f"structure and develop your content together.\n\n"
        )

        # Add welcome message to agent state if using LLM
        if self.use_llm:
            # Strip Rich markup for the agent state
            plain_welcome = welcome_message.replace("[bold yellow]", "").replace(
                "[/bold yellow]", ""
            )
            self.agent_state.add_message("assistant", plain_welcome)

        # Start with first question
        first_question = self.get_next_question()

        # Add first question to agent state if using LLM
        if self.use_llm:
            # Strip Rich markup for the agent state
            plain_question = first_question.replace("[bold green]", "").replace(
                "[/bold green]", ""
            )
            plain_question = plain_question.replace("[white]", "").replace(
                "[/white]", ""
            )
            self.agent_state.add_message("assistant", plain_question)

        # Format the welcome message with Rich styling
        formatted_welcome = f"[bold blue]Welcome![/bold blue]\n\n{welcome_message}"

        return formatted_welcome + first_question

    def display_message(self, message, style="info"):
        """Display a message with Rich styling."""
        if style == "info":
            self.console.print(Panel(message, border_style="blue"))
        elif style == "success":
            self.console.print(Panel(message, border_style="green"))
        elif style == "warning":
            self.console.print(Panel(message, border_style="yellow"))
        elif style == "error":
            self.console.print(Panel(message, border_style="red"))
        else:
            self.console.print(message)

    def display_markdown(self, markdown_text):
        """Display markdown formatted text."""
        markdown = Markdown(markdown_text)
        self.console.print(markdown)

    def save_state(self):
        """Save the current agent state for later resumption."""
        if not self.use_llm:
            return None

        return self.agent_state.save_state()

    def load_state(self, state_data):
        """Load a previously saved agent state."""
        if not self.use_llm or not state_data:
            return False

        try:
            self.agent_state.load_state(state_data)
            self.session_id = self.agent_state.session_id
            return True
        except Exception as e:
            self.logger.error(f"Error loading agent state: {e}", exc_info=True)
            return False
