# main.py
import logging
import sys
import os
from src.memory.graph_db import MemoryManager
from src.engine.phase import PhaseController
from src.engine.interaction import InteractionEngine
from src.interface.console import ConsoleInterface
from src.llm import LLMClient, PromptManager
from rich.logging import RichHandler


def setup_logging():
    """Set up logging configuration with Rich formatting."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.FileHandler("content_agent.log"),
            RichHandler(rich_tracebacks=True, markup=True),
        ],
    )


def main():
    """Main entry point for the application."""
    setup_logging()
    logger = logging.getLogger(__name__)

    memory = None  # Initialize to None for cleanup in finally block

    try:
        # Initialize components
        logger.info("Initializing memory manager...")
        memory = MemoryManager()

        logger.info("Initializing phase controller...")
        phase_controller = PhaseController(memory)

        # Check if we should use LLM
        use_llm = os.environ.get("USE_LLM", "false").lower() == "true"
        llm_client = None
        prompt_manager = None

        if use_llm:
            try:
                # Initialize LLM components
                logger.info("Initializing LLM client...")
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning(
                        "ANTHROPIC_API_KEY not set. LLM features will be disabled."
                    )
                    use_llm = False
                else:
                    llm_client = LLMClient(api_key=api_key)

                    logger.info("Initializing prompt manager...")
                    prompt_manager = PromptManager()

                    # Create prompt directory structure if it doesn't exist
                    prompt_manager.create_prompt_directory()
            except Exception as e:
                logger.error(f"Error initializing LLM components: {e}", exc_info=True)
                use_llm = False
                llm_client = None
                prompt_manager = None

        logger.info("Initializing interaction engine...")
        interaction = InteractionEngine(
            memory,
            phase_controller,
            llm_client=llm_client,
            prompt_manager=prompt_manager,
        )

        logger.info("Initializing console interface...")
        console = ConsoleInterface(interaction)

        # Start the interface
        logger.info(f"Starting console interface with LLM: {use_llm}...")
        console.start()

    except KeyboardInterrupt:
        # Handle Ctrl+C at the top level
        logger.info("Application interrupted by user.")
        print("\nApplication interrupted. Exiting gracefully...")

    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")

    finally:
        # Clean up resources
        logger.info("Shutting down application...")
        if memory:
            try:
                memory.close()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}", exc_info=True)


if __name__ == "__main__":
    main()
