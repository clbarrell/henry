# src/engine/interaction.py
import logging
import random


class InteractionEngine:
    """Manages the conversation flow and question generation."""

    def __init__(self, memory_manager, phase_controller):
        """Initialize with memory manager and phase controller."""
        self.memory = memory_manager
        self.phase_controller = phase_controller
        self.logger = logging.getLogger(__name__)
        self.last_question_id = None

    def process_user_input(self, text):
        """Process user input and determine next agent action."""
        # Store the user input
        input_id = self.memory.add_user_input(text, self.last_question_id)
        self.logger.info(f"Stored user input: {text[:50]}...")

        # Check for commands
        if text.startswith("/"):
            return self._handle_command(text)

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
            return (
                "Available commands:\n"
                "/help - Show this help message\n"
                "/status - Show the current phase and progress\n"
                "/export - Export the content\n"
                "/next - Move to the next phase"
            )

        elif command == "/status":
            current_phase = self.phase_controller.get_current_phase()
            phase_name = self.phase_controller.reverse_phase_map[current_phase]
            return f"Current phase: {phase_name}"

        elif command == "/export":
            # Simplified export functionality
            return "Content export would happen here (not implemented in MVP)"

        elif command == "/next":
            if self.phase_controller.transition_to_next_phase():
                return f"Moving to {self.phase_controller.get_current_phase().name} phase.\n\n{self.get_next_question()}"
            else:
                return "Cannot transition to next phase. You may already be in the final phase."

        else:
            return f"Unknown command: {command}. Type /help for available commands."

    def get_next_question(self):
        """Generate the next question based on the current phase and context."""
        current_phase = self.phase_controller.get_current_phase()
        phase_prompts = self.phase_controller.get_phase_prompts()

        question = random.choice(phase_prompts)
        question_id = self.memory.add_question(question, intent=current_phase.name)
        self.last_question_id = question_id

        return question

    def start_session(self, content_type, topic):
        """Start a new content creation session."""
        self.memory.start_new_session(content_type, topic)

        welcome_message = (
            f"Welcome to your {content_type} creation session about '{topic}'!\n\n"
            f"We'll start by gathering some context about what you want to write. "
            f"I'll ask you questions to help organize your thoughts, and then we'll "
            f"structure and develop your content together.\n\n"
        )

        # Start with first question
        return welcome_message + self.get_next_question()
