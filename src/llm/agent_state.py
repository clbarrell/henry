from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging


@dataclass
class Message:
    """Represents a message in the conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API."""
        return {"role": self.role, "content": self.content}

    def to_storage_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_storage_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a Message from a storage dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class AgentState:
    """Manages the agent's state and conversation context."""

    def __init__(self, max_context_messages=10):
        """Initialize the agent state.

        Args:
            max_context_messages: Maximum number of messages to keep in context
        """
        self.max_context_messages = max_context_messages
        self.recent_messages: List[Message] = []
        self.current_topic: Optional[str] = None
        self.content_type: Optional[str] = None
        self.session_id: Optional[str] = None
        self.confidence: Dict[str, float] = {}
        self.working_memory: Dict[str, Any] = {}
        self.last_analysis: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the recent messages list.

        Args:
            role: The role of the message sender ("user" or "assistant")
            content: The content of the message
            metadata: Optional metadata for the message
        """
        self.recent_messages.append(
            Message(role=role, content=content, metadata=metadata or {})
        )

        # Trim to max context if needed
        if len(self.recent_messages) > self.max_context_messages:
            self.recent_messages = self.recent_messages[-self.max_context_messages :]

    def get_recent_context(self) -> List[Dict[str, str]]:
        """Get recent messages in a format suitable for Claude API.

        Returns:
            List of message dictionaries with role and content
        """
        return [msg.to_dict() for msg in self.recent_messages]

    def set_analysis_result(self, analysis: Dict[str, Any]):
        """Store the latest analysis from the LLM.

        Args:
            analysis: Analysis results from the LLM
        """
        self.last_analysis = analysis

        # Update confidence values if provided
        if "confidence" in analysis:
            self.confidence.update(analysis["confidence"])

        # Update working memory with any extracted entities or insights
        if "entities" in analysis:
            self.working_memory["entities"] = analysis["entities"]

        if "intent" in analysis:
            self.working_memory["intent"] = analysis["intent"]

        if "sentiment" in analysis:
            self.working_memory["sentiment"] = analysis["sentiment"]

    def get_phase_confidence(self, phase_name: str) -> float:
        """Get confidence level for a specific phase.

        Args:
            phase_name: Name of the phase

        Returns:
            Confidence level (0.0 to 1.0)
        """
        return self.confidence.get(f"phase_{phase_name.lower()}", 0.0)

    def save_state(self) -> Dict[str, Any]:
        """Save the agent state to a dictionary for persistence.

        Returns:
            Dictionary representation of the agent state
        """
        return {
            "session_id": self.session_id,
            "current_topic": self.current_topic,
            "content_type": self.content_type,
            "confidence": self.confidence,
            "working_memory": self.working_memory,
            "recent_messages": [msg.to_storage_dict() for msg in self.recent_messages],
        }

    def load_state(self, state_data: Dict[str, Any]):
        """Load the agent state from a dictionary.

        Args:
            state_data: Dictionary representation of the agent state
        """
        self.session_id = state_data.get("session_id")
        self.current_topic = state_data.get("current_topic")
        self.content_type = state_data.get("content_type")
        self.confidence = state_data.get("confidence", {})
        self.working_memory = state_data.get("working_memory", {})

        # Load messages
        self.recent_messages = []
        for msg_data in state_data.get("recent_messages", []):
            try:
                self.recent_messages.append(Message.from_storage_dict(msg_data))
            except Exception as e:
                self.logger.error(f"Error loading message: {e}")

    def reset(self):
        """Reset the agent state for a new session."""
        self.recent_messages = []
        self.current_topic = None
        self.content_type = None
        self.session_id = None
        self.confidence = {}
        self.working_memory = {}
        self.last_analysis = {}
