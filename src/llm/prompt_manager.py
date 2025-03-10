import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class PromptManager:
    """Manages prompt templates for the LLM."""

    def __init__(self, prompts_dir="prompts"):
        """Initialize the prompt manager.

        Args:
            prompts_dir: Directory containing prompt templates
        """
        self.prompts_dir = Path(prompts_dir)
        self.prompts = {}
        self.default_prompts = self._get_default_prompts()
        self.logger = logging.getLogger(__name__)

        # Try to load prompts from files if directory exists
        if self.prompts_dir.exists():
            self._load_prompts()
        else:
            self.logger.warning(
                f"Prompts directory {prompts_dir} not found. Using default prompts."
            )

    def _load_prompts(self):
        """Load all prompt templates from files."""
        for prompt_file in self.prompts_dir.glob("**/*.txt"):
            relative_path = prompt_file.relative_to(self.prompts_dir)
            prompt_name = str(relative_path).replace(".txt", "").replace("/", ".")
            try:
                with open(prompt_file, "r") as f:
                    self.prompts[prompt_name] = f.read()
            except Exception as e:
                self.logger.error(f"Error loading prompt {prompt_name}: {e}")

    def _get_default_prompts(self) -> Dict[str, str]:
        """Get default prompts to use if files are not available."""
        return {
            "base": """
            You are a Content Creation Assistant that helps users create high-quality content through a structured process.
            You guide users through four phases:
            1. Context Gathering - Understanding the topic, audience, and goals
            2. Structure Development - Creating an outline and organization
            3. Content Development - Expanding sections with details
            4. Refinement - Polishing and finalizing
            
            Your job is to ask relevant questions, analyze responses, and guide the user through this process.
            """,
            "phases.context_gathering": """
            You are in the Context Gathering phase of content creation.
            
            In this phase, your goal is to understand:
            - The topic and main ideas
            - The target audience
            - The purpose and goals of the content
            - The tone and style preferences
            - Any specific requirements or constraints
            
            Ask focused questions to gather this information. Be conversational but purposeful.
            """,
            "phases.structure_development": """
            You are in the Structure Development phase of content creation.
            
            In this phase, your goal is to help the user:
            - Create a logical outline for their content
            - Organize their ideas in a coherent flow
            - Identify main sections and subsections
            - Determine the right structure for their content type
            
            Ask questions that help the user think about organization and structure.
            """,
            "phases.content_development": """
            You are in the Content Development phase of content creation.
            
            In this phase, your goal is to help the user:
            - Expand each section with supporting details
            - Develop compelling arguments or explanations
            - Add examples, evidence, or stories
            - Create engaging content for each part of the structure
            
            Focus on one section at a time and ask questions that help the user develop rich content.
            """,
            "phases.refinement": """
            You are in the Refinement phase of content creation.
            
            In this phase, your goal is to help the user:
            - Review and improve their content
            - Ensure consistency in tone and style
            - Strengthen weak areas
            - Polish the final product
            
            Ask questions that help the user critically evaluate and improve their content.
            """,
        }

    def get_prompt(self, name: str, **kwargs) -> str:
        """Get a prompt template and format it with kwargs.

        Args:
            name: Name of the prompt template
            **kwargs: Variables to format the prompt with

        Returns:
            Formatted prompt template
        """
        # Try to get from loaded prompts first, then fall back to defaults
        prompt_template = self.prompts.get(name)
        if prompt_template is None:
            prompt_template = self.default_prompts.get(name)
            if prompt_template is None:
                self.logger.warning(f"Prompt '{name}' not found, using generic prompt")
                return self.default_prompts.get("base", "You are a helpful assistant.")

        # Format the prompt with kwargs
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing key in prompt formatting: {e}")
            return prompt_template  # Return unformatted prompt if formatting fails

    def create_prompt_directory(self):
        """Create the prompts directory structure if it doesn't exist."""
        if not self.prompts_dir.exists():
            try:
                # Create main prompts directory
                self.prompts_dir.mkdir(parents=True, exist_ok=True)

                # Create phases subdirectory
                phases_dir = self.prompts_dir / "phases"
                phases_dir.mkdir(exist_ok=True)

                # Create functions subdirectory
                functions_dir = self.prompts_dir / "functions"
                functions_dir.mkdir(exist_ok=True)

                # Write default prompts to files
                for name, content in self.default_prompts.items():
                    parts = name.split(".")
                    if len(parts) > 1:
                        # Create nested path
                        file_path = self.prompts_dir
                        for part in parts[:-1]:
                            file_path = file_path / part
                            file_path.mkdir(exist_ok=True)
                        file_path = file_path / f"{parts[-1]}.txt"
                    else:
                        file_path = self.prompts_dir / f"{name}.txt"

                    with open(file_path, "w") as f:
                        f.write(content.strip())

                self.logger.info(f"Created prompts directory at {self.prompts_dir}")
                return True
            except Exception as e:
                self.logger.error(f"Error creating prompts directory: {e}")
                return False
        return True
