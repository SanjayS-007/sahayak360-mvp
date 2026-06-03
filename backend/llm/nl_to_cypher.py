"""
NL-to-Cypher — Converts natural language questions to Neo4j Cypher via Gemini.
Includes safety validation to prevent write operations.
"""

import logging
from pathlib import Path
from typing import Optional

from llm.gemini_client import generate_json
from config import settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "nl_to_cypher.txt"

# Disallowed Cypher keywords (write operations)
WRITE_KEYWORDS = {"CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP"}


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def validate_cypher_safety(cypher: str) -> bool:
    """Ensure generated Cypher is read-only. Returns True if safe."""
    upper = cypher.upper()
    for keyword in WRITE_KEYWORDS:
        if keyword in upper:
            return False
    return True


async def nl_to_cypher(
    question: str,
    user_id: str,
    role: str = "teacher",
    class_section: str = "",
) -> dict:
    """
    Convert natural language question to Cypher query.
    Returns: {"cypher": "...", "params": {...}, "explanation": "..."}
    Raises ValueError if generation fails or query is unsafe.
    """
    prompt_template = _load_prompt()
    prompt = prompt_template.replace("{question}", question)
    prompt = prompt.replace("{role}", role)
    prompt = prompt.replace("{user_id}", user_id)
    prompt = prompt.replace("{class_section}", class_section)

    try:
        result = await generate_json(prompt)
    except (ValueError, RuntimeError) as e:
        logger.error(f"NL-to-Cypher generation failed: {e}")
        raise ValueError(f"Could not generate query: {e}")

    # Check for error response from LLM
    if "error" in result:
        raise ValueError(result["error"])

    cypher = result.get("cypher", "")
    if not cypher:
        raise ValueError("No Cypher query generated")

    # Safety validation
    if not validate_cypher_safety(cypher):
        logger.warning(f"BLOCKED unsafe Cypher: {cypher}")
        raise ValueError("Generated query contains write operations and was blocked for safety")

    return {
        "cypher": cypher,
        "params": result.get("params", {}),
        "explanation": result.get("explanation", ""),
    }


async def execute_nl_query(
    question: str,
    user_id: str,
    role: str,
    class_section: str,
    neo4j_driver,
) -> dict:
    """
    Full pipeline: NL question → Cypher → Execute → Format response.
    """
    # Step 1: Generate Cypher
    query_data = await nl_to_cypher(question, user_id, role, class_section)

    # Step 2: Execute against Neo4j
    cypher = query_data["cypher"]
    params = query_data["params"]

    try:
        async with neo4j_driver.session(database=settings.NEO4J_DATABASE) as session:
            result = await session.run(cypher, **params)
            records = [record.data() async for record in result]
    except Exception as e:
        logger.error(f"Cypher execution failed: {e}")
        raise ValueError(f"Query execution failed: {e}")

    # Step 3: Format response
    return {
        "answer": query_data["explanation"],
        "data": records[:50],  # Limit results
        "cypher_used": cypher,
        "record_count": len(records),
    }
