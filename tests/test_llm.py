#!/usr/bin/env python3
"""
Test script for LLM integration.
This script tests the basic functionality of the LLM integration.
"""

import os
import logging
from src.llm import LLMClient, PromptManager, AgentState

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_llm_client():
    """Test the LLM client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set. Please set it to run this test.")
        return False

    try:
        # Initialize LLM client
        logger.info("Initializing LLM client...")
        llm_client = LLMClient(api_key=api_key)

        # Test simple response generation
        logger.info("Testing simple response generation...")
        response = llm_client.generate_response(
            messages=[{"role": "user", "content": "Hello, Claude!"}],
            system="You are a helpful assistant.",
            max_tokens=100,
        )

        logger.info(f"Response: {response.content[0].text}")

        # Test question generation
        logger.info("Testing question generation...")
        question = llm_client.generate_question(
            conversation_context=[
                {"role": "user", "content": "I want to write a blog post about AI."}
            ],
            system_prompt="You are a content creation assistant.",
            current_phase="Context Gathering",
        )

        logger.info(f"Generated question: {question}")

        # Test input analysis
        logger.info("Testing input analysis...")
        analysis = llm_client.analyze_input(
            conversation_context=[
                {
                    "role": "assistant",
                    "content": "What's your target audience for this blog post?",
                },
                {
                    "role": "user",
                    "content": "My target audience is technical professionals who are interested in AI but don't have a deep background in it.",
                },
            ],
            system_prompt="You are a content creation assistant.",
            current_phase="Context Gathering",
        )

        logger.info(f"Analysis result: {analysis}")

        return True
    except Exception as e:
        logger.error(f"Error testing LLM client: {e}", exc_info=True)
        return False


def test_prompt_manager():
    """Test the prompt manager."""
    try:
        # Initialize prompt manager
        logger.info("Initializing prompt manager...")
        prompt_manager = PromptManager()

        # Create prompt directory
        logger.info("Creating prompt directory...")
        prompt_manager.create_prompt_directory()

        # Test getting prompts
        logger.info("Testing prompt retrieval...")
        base_prompt = prompt_manager.get_prompt("base")
        logger.info(f"Base prompt: {base_prompt[:100]}...")

        context_prompt = prompt_manager.get_prompt("phases.context_gathering")
        logger.info(f"Context gathering prompt: {context_prompt[:100]}...")

        return True
    except Exception as e:
        logger.error(f"Error testing prompt manager: {e}", exc_info=True)
        return False


def test_agent_state():
    """Test the agent state."""
    try:
        # Initialize agent state
        logger.info("Initializing agent state...")
        agent_state = AgentState()

        # Add messages
        logger.info("Adding messages...")
        agent_state.add_message("user", "Hello, I want to write a blog post about AI.")
        agent_state.add_message("assistant", "Great! What's your target audience?")
        agent_state.add_message("user", "Technical professionals interested in AI.")

        # Get conversation context
        logger.info("Getting conversation context...")
        context = agent_state.get_recent_context()
        logger.info(f"Context: {context}")

        # Test save and load
        logger.info("Testing save and load...")
        state_data = agent_state.save_state()

        new_agent_state = AgentState()
        new_agent_state.load_state(state_data)

        new_context = new_agent_state.get_recent_context()
        logger.info(f"Loaded context: {new_context}")

        return True
    except Exception as e:
        logger.error(f"Error testing agent state: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Testing LLM integration...")

    llm_result = test_llm_client()
    prompt_result = test_prompt_manager()
    state_result = test_agent_state()

    if llm_result and prompt_result and state_result:
        logger.info("All tests passed!")
    else:
        logger.error("Some tests failed.")
        if not llm_result:
            logger.error("LLM client test failed.")
        if not prompt_result:
            logger.error("Prompt manager test failed.")
        if not state_result:
            logger.error("Agent state test failed.")
