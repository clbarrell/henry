# src/engine/phase.py
import logging
from enum import Enum, auto

class ContentPhase(Enum):
    """Enumeration of content creation phases."""
    CONTEXT_GATHERING = auto()
    STRUCTURE_DEVELOPMENT = auto()
    CONTENT_DEVELOPMENT = auto()
    REFINEMENT = auto()

class PhaseController:
    """Controls the transitions between different phases of content creation."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager."""
        self.memory = memory_manager
        self.logger = logging.getLogger(__name__)
        self.phase_map = {
            "Context Gathering": ContentPhase.CONTEXT_GATHERING,
            "Structure Development": ContentPhase.STRUCTURE_DEVELOPMENT,
            "Content Development": ContentPhase.CONTENT_DEVELOPMENT,
            "Refinement": ContentPhase.REFINEMENT
        }
        self.reverse_phase_map = {v: k for k, v in self.phase_map.items()}
    
    def get_current_phase(self):
        """Get the current phase as an enum."""
        phase_name = self.memory.get_current_phase()
        return self.phase_map.get(phase_name)
    
    def transition_to_next_phase(self):
        """Transition to the next phase in the sequence."""
        current_phase = self.get_current_phase()
        
        if current_phase == ContentPhase.CONTEXT_GATHERING:
            next_phase = ContentPhase.STRUCTURE_DEVELOPMENT
        elif current_phase == ContentPhase.STRUCTURE_DEVELOPMENT:
            next_phase = ContentPhase.CONTENT_DEVELOPMENT
        elif current_phase == ContentPhase.CONTENT_DEVELOPMENT:
            next_phase = ContentPhase.REFINEMENT
        else:
            self.logger.warning("Already in the final phase or unknown phase")
            return False
        
        phase_name = self.reverse_phase_map[next_phase]
        self.memory.transition_phase(phase_name)
        self.logger.info(f"Transitioned to phase: {phase_name}")
        return True
    
    def get_phase_prompts(self):
        """Get prompts/questions associated with the current phase."""
        current_phase = self.get_current_phase()
        
        if current_phase == ContentPhase.CONTEXT_GATHERING:
            return [
                "What topic would you like to write about?",
                "Who is your target audience for this content?",
                "What are the key points you want to address?",
                "What is the purpose of this content? (Educate, entertain, persuade, etc.)",
                "Are there any specific examples or stories you want to include?"
            ]
        
        elif current_phase == ContentPhase.STRUCTURE_DEVELOPMENT:
            return [
                "Based on our discussion, I think these sections would work well. What do you think?",
                "Would you like to adjust the order of these sections?",
                "Do you have a preference for how to introduce this topic?",
                "How would you like to conclude this piece?",
                "Should we include any additional sections?"
            ]
        
        elif current_phase == ContentPhase.CONTENT_DEVELOPMENT:
            return [
                "Let's expand on the first section. What details should we include?",
                "Can you provide more information or examples for this point?",
                "Is there any research or data that would strengthen this argument?",
                "How would you explain this concept to someone unfamiliar with the topic?",
                "Should we include any personal experiences related to this point?"
            ]
        
        elif current_phase == ContentPhase.REFINEMENT:
            return [
                "Does the flow of the content feel natural to you?",
                "Are there any sections that need more development?",
                "Is the tone consistent throughout?",
                "Does the introduction effectively hook the reader?",
                "Does the conclusion provide a satisfying ending?"
            ]
        
        return ["Could you tell me more about what you're looking to create?"]