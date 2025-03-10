# Content Creation AI Agent

A smart AI assistant that guides users through the process of creating blog posts, Twitter threads, and LinkedIn content by asking targeted questions, maintaining context, and providing structured guidance.

## Overview

The Content Creation AI Agent helps overcome writer's block and streamline content creation by breaking the process into manageable phases:

1. **Context Gathering** - Collects information about your topic, audience, and goals
2. **Structure Development** - Helps organize your ideas into a coherent outline
3. **Content Development** - Guides you through expanding each section with supporting details
4. **Refinement** - Helps polish and finalize your content

The agent maintains context throughout the conversation, asks relevant questions to move the process forward, and stores all information in a graph database for powerful relationship mapping between ideas.

## Installation

### Prerequisites

- Python 3.9 or higher
- Neo4j Database (local installation or cloud instance)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/content-creation-agent.git
   cd content-creation-agent
   ```

2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure Neo4j:
   - Install Neo4j Desktop from [neo4j.com/download](https://neo4j.com/download/)
   - Create a new database with a password
   - Update the Neo4j connection details in `main.py` if needed:
     ```python
     memory = MemoryManager(uri="bolt://localhost:7687", username="neo4j", password="your_password")
     ```

## Usage

1. Start the application:

   ```bash
   python main.py
   ```

2. Follow the prompts to:
   - Select the type of content you want to create
   - Provide your topic
   - Answer the agent's questions to develop your content

### Commands

The following commands are available during any content creation session:

- `/help` - Show available commands
- `/status` - Display current phase and progress
- `/export` - Export your content (coming soon)
- `/next` - Manually transition to the next phase
- `exit` - End the session and quit the application

## Features

- **Structured Writing Process**: Guides you through a proven content creation workflow
- **Persistent Memory**: Uses Neo4j graph database to maintain context and relationships between ideas
- **Phase-Based Guidance**: Different question strategies for each phase of content creation
- **Contextual Understanding**: Analyzes your responses to ask relevant follow-up questions
- **Command Interface**: Simple commands to control the application flow

## Project Structure

```
content_creation_agent/
├── main.py                  # Entry point
├── src/
│   ├── memory/              # Neo4j integration
│   │   └── graph_db.py      # Memory management
│   ├── engine/              # Core functionality
│   │   ├── phase.py         # Phase controller
│   │   └── interaction.py   # Interaction engine
│   ├── interface/           # User interaction
│   │   └── console.py       # Console interface
│   └── utils/               # Helper functions
└── tests/                   # Test suite
    ├── test_memory.py       # Memory tests
    └── test_interaction.py  # Interaction tests
```

## Technical Details

### Memory Model

Content is stored in a graph structure with the following key relationships:

- Content → Phase → Section → Point → Evidence
- UserInput → Question
- Content → UserInput

This graph structure allows the agent to understand the relationships between different pieces of information and track the writing process effectively.

### Phase Controller

The phase controller manages transitions between the four phases of content creation and provides appropriate guidance for each phase.

### Testing

Run the test suite with:

```bash
pytest tests/
```

The tests verify the core functionality of the memory management system and interaction engine.

## Future Roadmap

- Web interface for more user-friendly interaction
- Export to various formats (Markdown, HTML, direct platform posting)
- Templates for different content types and styles
- Integration with SEO tools and content analyzers
- Multi-modal content suggestions (images, video concepts)

## License

MIT License

---

**Note**: This is an MVP version focused on core functionality. Some features mentioned in the design document are planned for future implementation.
