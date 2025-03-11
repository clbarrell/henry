import os
import logging
import anthropic
from typing import List, Dict, Any, Optional


class LLMClient:
    """Client for interacting with Anthropic's Claude API."""

    def __init__(self, api_key=None, model="claude-3-7-sonnet-latest"):
        """Initialize the LLM client with API key and model."""
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = model
        self.logger = logging.getLogger(__name__)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Generate a response from Claude.

        Args:
            messages: List of message objects with role and content
            system: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            The complete response from the API
        """
        try:
            # Clean messages to remove trailing whitespace and filter out empty messages
            cleaned_messages = []
            for msg in messages:
                cleaned_msg = msg.copy()
                if "content" in cleaned_msg:
                    if isinstance(cleaned_msg["content"], str):
                        cleaned_msg["content"] = cleaned_msg["content"].strip()
                        # Skip messages with empty content
                        if not cleaned_msg["content"]:
                            continue
                    elif isinstance(cleaned_msg["content"], list):
                        # Handle content that might be a list of content blocks
                        cleaned_content = []
                        for content_item in cleaned_msg["content"]:
                            if (
                                isinstance(content_item, dict)
                                and "text" in content_item
                            ):
                                content_item["text"] = content_item["text"].strip()
                            cleaned_content.append(content_item)
                        cleaned_msg["content"] = cleaned_content
                cleaned_messages.append(cleaned_msg)

            # Ensure we have at least one message
            if not cleaned_messages:
                self.logger.warning(
                    "No valid messages to send to API, adding default message"
                )
                cleaned_messages = [{"role": "user", "content": "Hello"}]

            # Clean system prompt if provided
            if system:
                system = system.strip()

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=cleaned_messages,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise

    def analyze_input(
        self,
        conversation_context: List[Dict[str, str]],
        system_prompt: str,
        current_phase: str,
    ) -> Dict[str, Any]:
        """Analyze user input to determine intent, entities, and phase transition.

        Args:
            conversation_context: Recent conversation messages
            system_prompt: System prompt for the current phase
            current_phase: Current content creation phase

        Returns:
            Dictionary with analysis results
        """
        analysis_prompt = f"""
        {system_prompt}
        
        Your task is to analyze the user's input and determine:
        1. Key entities and concepts mentioned
        2. User's intent and sentiment
        3. Whether enough information has been gathered to move to the next phase
        4. Confidence level in current phase completion (0.0 to 1.0)
        
        Current phase: {current_phase}
        
        Format your response as JSON:
        {{
            "entities": ["entity1", "entity2"],
            "intent": "user's primary intent",
            "sentiment": "positive/negative/neutral",
            "should_transition": true/false,
            "transition_message": "Message explaining phase transition",
            "confidence": {{"phase_completion": 0.85}}
        }}
        """

        try:
            response = self.generate_response(
                messages=conversation_context, system=analysis_prompt, max_tokens=1024
            )

            # Extract JSON from response
            content_text = response.content[0].text
            import json

            analysis_result = json.loads(content_text)
            return analysis_result
        except Exception as e:
            self.logger.error(f"Error analyzing input: {e}")
            # Return a default analysis if there's an error
            return {
                "entities": [],
                "intent": "unknown",
                "sentiment": "neutral",
                "should_transition": False,
                "transition_message": "",
                "confidence": {"phase_completion": 0.0},
            }

    def generate_question(
        self,
        conversation_context: List[Dict[str, str]],
        system_prompt: str,
        current_phase: str,
    ) -> str:
        """Generate the next question based on conversation context.

        Args:
            conversation_context: Recent conversation messages
            system_prompt: System prompt for the current phase
            current_phase: Current content creation phase

        Returns:
            Generated question
        """
        question_prompt = f"""
        {system_prompt}
        
        Your task is to generate the next question to ask the user.
        The question should be relevant to the current phase ({current_phase}) 
        and should help gather more information or clarify existing information.
        
        Generate a single, clear question that will help move the content creation process forward.
        """.strip()

        try:
            response = self.generate_response(
                messages=conversation_context, system=question_prompt, max_tokens=512
            )
            return response.content[0].text.strip()
        except Exception as e:
            self.logger.error(f"Error generating question: {e}")
            # Return a default question if there's an error
            return f"Could you tell me more about your content for the {current_phase} phase?"
