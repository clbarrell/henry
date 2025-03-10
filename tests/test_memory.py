# tests/test_memory.py
import pytest
from src.memory.graph_db import MemoryManager

class TestMemoryManager:
    """Tests for the MemoryManager class."""
    
    @pytest.fixture
    def memory_manager(self):
        """Set up a memory manager for testing."""
        mm = MemoryManager(uri="bolt://localhost:7687", username="neo4j", password="password")
        yield mm
        mm.close()
    
    def test_start_new_session(self, memory_manager):
        """Test starting a new session."""
        session_id = memory_manager.start_new_session("blog_post", "Test Topic")
        assert session_id is not None
        
        phase = memory_manager.get_current_phase()
        assert phase == "Context Gathering"
    
    def test_add_section_and_point(self, memory_manager):
        """Test adding sections and points to the content structure."""
        session_id = memory_manager.start_new_session("blog_post", "Test Topic")
        
        section_id = memory_manager.add_section("Introduction")
        
        structure = memory_manager.get_content_structure()
        assert "Introduction" in structure
    
    def test_phase_transition(self, memory_manager):
        """Test transitioning between phases."""
        session_id = memory_manager.start_new_session("blog_post", "Test Topic")
        
        initial_phase = memory_manager.get_current_phase()
        assert initial_phase == "Context Gathering"
        
        memory_manager.transition_phase("Structure Development")
        new_phase = memory_manager.get_current_phase()
        assert new_phase == "Structure Development"