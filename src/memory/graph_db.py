# src/memory/graph_db.py
from neo4j import GraphDatabase
import logging


class MemoryManager:
    """Manages the graph database for storing content structure and context."""

    def __init__(
        self, uri="bolt://localhost:7687", username="neo4j", password="password"
    ):
        """Initialize connection to Neo4j database."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.session_id = None
        self.logger = logging.getLogger(__name__)
        self._ensure_constraints()

    def _ensure_constraints(self):
        """Create necessary constraints and indexes."""
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Content) REQUIRE c.id IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Phase) REQUIRE p.id IS UNIQUE"
            )
            session.run("CREATE INDEX IF NOT EXISTS FOR (p:Point) ON (p.text)")

    def start_new_session(self, content_type, topic):
        """Start a new content creation session."""
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (c:Content {id: randomUUID(), type: $type, topic: $topic, created: datetime()})
                CREATE (p:Phase {id: randomUUID(), name: 'Context Gathering', started: datetime()})
                CREATE (c)-[:CURRENT_PHASE]->(p)
                RETURN c.id as content_id, p.id as phase_id
                """,
                type=content_type,
                topic=topic,
            )
            record = result.single()
            self.session_id = record["content_id"]
            self.current_phase_id = record["phase_id"]
            return self.session_id

    def add_user_input(self, text, response_to=None):
        """Store user input in the graph."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Content {id: $content_id})
                CREATE (i:UserInput {id: randomUUID(), text: $text, timestamp: datetime()})
                CREATE (c)-[:HAS_INPUT]->(i)
                RETURN i.id as input_id
                """,
                content_id=self.session_id,
                text=text,
            )
            input_id = result.single()["input_id"]

            if response_to:
                session.run(
                    """
                    MATCH (i:UserInput {id: $input_id})
                    MATCH (q:Question {id: $question_id})
                    CREATE (i)-[:RESPONSE_TO]->(q)
                    """,
                    input_id=input_id,
                    question_id=response_to,
                )

            return input_id

    def add_question(self, text, intent=None):
        """Store a question in the graph."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (c:Content {id: $content_id})
                    MATCH (p:Phase {id: $phase_id})
                    CREATE (q:Question {id: randomUUID(), text: $text, intent: $intent, timestamp: datetime()})
                    CREATE (c)-[:HAS_QUESTION]->(q)
                    CREATE (p)-[:ASKED]->(q)
                    RETURN q.id as question_id
                    """,
                    content_id=self.session_id,
                    phase_id=self.current_phase_id,
                    text=text,
                    intent=intent,
                )
                return result.single()["question_id"]
        except Exception as e:
            self.logger.error(f"Failed to add question '{text}': {e}")
            raise

    def add_section(self, title):
        """Add a content section."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Content {id: $content_id})
                CREATE (s:Section {id: randomUUID(), title: $title, created: datetime()})
                CREATE (c)-[:HAS_SECTION]->(s)
                RETURN s.id as section_id
                """,
                content_id=self.session_id,
                title=title,
            )
            return result.single()["section_id"]

    def get_content_structure(self):
        """Get the current content structure."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Content {id: $content_id})-[:HAS_SECTION]->(s:Section)
                OPTIONAL MATCH (s)-[:CONTAINS]->(p:Point)
                OPTIONAL MATCH (p)-[:SUPPORTED_BY]->(e:Evidence)
                RETURN s.title as section, collect({
                    point: p.text,
                    evidence: collect(e.text)
                }) as points
                """,
                content_id=self.session_id,
            )
            structure = {}
            for record in result:
                section_title = record["section"]
                points = record["points"]
                if section_title not in structure:
                    structure[section_title] = []

                for point_data in points:
                    if point_data["point"]:
                        structure[section_title].append(
                            {
                                "text": point_data["point"],
                                "evidence": [e for e in point_data["evidence"] if e],
                            }
                        )

            return structure

    def transition_phase(self, new_phase_name):
        """Transition to a new phase."""
        with self.driver.session() as session:
            # End current phase
            session.run(
                """
                MATCH (c:Content {id: $content_id})-[r:CURRENT_PHASE]->(p:Phase)
                SET p.ended = datetime()
                DELETE r
                """,
                content_id=self.session_id,
            )

            # Create new phase and set as current
            result = session.run(
                """
                MATCH (c:Content {id: $content_id})
                CREATE (p:Phase {id: randomUUID(), name: $phase_name, started: datetime()})
                CREATE (c)-[:CURRENT_PHASE]->(p)
                RETURN p.id as phase_id
                """,
                content_id=self.session_id,
                phase_name=new_phase_name,
            )
            self.current_phase_id = result.single()["phase_id"]
            return self.current_phase_id

    def get_current_phase(self):
        """Get the current phase of content creation."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Content {id: $content_id})-[:CURRENT_PHASE]->(p:Phase)
                RETURN p.name as phase_name
                """,
                content_id=self.session_id,
            )
            record = result.single()
            return record["phase_name"] if record else None

    def list_sessions(self):
        """List all available content sessions.

        Returns:
            List of dictionaries containing session information
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Content)
                OPTIONAL MATCH (c)-[:CURRENT_PHASE]->(p:Phase)
                RETURN c.id as id, c.topic as topic, c.type as type, 
                       c.created as created, p.name as current_phase
                ORDER BY c.created DESC
                """
            )

            sessions = []
            for record in result:
                sessions.append(
                    {
                        "id": record["id"],
                        "topic": record["topic"],
                        "type": record["type"],
                        "created": record["created"],
                        "current_phase": record["current_phase"],
                    }
                )

            return sessions

    def load_session(self, session_id):
        """Load an existing session.

        Args:
            session_id: ID of the session to load

        Returns:
            Dictionary with session information or None if not found
        """
        with self.driver.session() as session:
            # First get the session and phase info
            result = session.run(
                """
                MATCH (c:Content {id: $session_id})
                OPTIONAL MATCH (c)-[:CURRENT_PHASE]->(p:Phase)
                RETURN c.id as content_id, c.topic as topic, c.type as type,
                       p.id as phase_id, p.name as phase_name
                """,
                session_id=session_id,
            )

            record = result.single()
            if not record:
                return None

            self.session_id = record["content_id"]
            self.current_phase_id = record["phase_id"]

            # Now get the last question if it exists
            question_result = session.run(
                """
                MATCH (c:Content {id: $content_id})-[:HAS_QUESTION]->(q:Question)
                RETURN q.id as question_id, q.text as question_text
                ORDER BY q.timestamp DESC
                LIMIT 1
                """,
                content_id=self.session_id,
            )

            question_record = question_result.single()

            # Create the session data dictionary
            session_data = {
                "id": record["content_id"],
                "topic": record["topic"],
                "type": record["type"],
                "phase_name": record["phase_name"],
                "last_question_id": (
                    question_record["question_id"] if question_record else None
                ),
                "last_question": (
                    question_record["question_text"] if question_record else None
                ),
            }

            return session_data

    def close(self):
        """Close the database connection."""
        self.driver.close()
