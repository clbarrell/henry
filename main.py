# main.py
import logging
import sys
from src.memory.graph_db import MemoryManager
from src.engine.phase import PhaseController
from src.engine.interaction import InteractionEngine
from src.interface.console import ConsoleInterface


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("content_agent.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    """Main entry point for the application."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize components
        logger.info("Initializing memory manager...")
        memory = MemoryManager()

        logger.info("Initializing phase controller...")
        phase_controller = PhaseController(memory)

        logger.info("Initializing interaction engine...")
        interaction = InteractionEngine(memory, phase_controller)

        logger.info("Initializing console interface...")
        console = ConsoleInterface(interaction)

        # Start the interface
        logger.info("Starting console interface...")
        console.start()

    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)

    finally:
        # Clean up resources
        logger.info("Shutting down application...")
        if "memory" in locals():
            memory.close()


if __name__ == "__main__":
    main()
