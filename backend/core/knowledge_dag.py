"""
Knowledge DAG — Directed Acyclic Graph for competency relationships.
Manages prerequisite chains, mastery state, and gap propagation.
Interfaces with Neo4j for persistence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config import settings


class MasteryLevel(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    BELOW_BASIC = "below_basic"
    BASIC = "basic"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"


@dataclass
class KnowledgeNode:
    kc_id: str
    name: str
    subject: str
    grade_level: int
    bloom_level: str  # remember, understand, apply, analyze, evaluate, create
    prerequisites: list[str] = field(default_factory=list)
    mastery: float = 0.0  # 0.0 to 1.0
    mastery_level: MasteryLevel = MasteryLevel.NOT_ATTEMPTED
    attempts: int = 0


@dataclass
class DAGEdge:
    from_kc: str
    to_kc: str
    weight: float = 1.0
    relationship: str = "PREREQUISITE_OF"


def mastery_to_level(mastery: float) -> MasteryLevel:
    """Convert mastery float (0-1) to categorical level."""
    if mastery < 0.01:
        return MasteryLevel.NOT_ATTEMPTED
    elif mastery < 0.40:
        return MasteryLevel.BELOW_BASIC
    elif mastery < 0.65:
        return MasteryLevel.BASIC
    elif mastery < 0.85:
        return MasteryLevel.PROFICIENT
    else:
        return MasteryLevel.ADVANCED


def compute_prerequisite_gap(
    target_node: KnowledgeNode,
    prerequisite_nodes: list[KnowledgeNode],
    threshold: float = 0.65,
) -> list[str]:
    """
    Identify prerequisite KCs that haven't been mastered.
    Returns list of KC IDs that are blocking the target node.
    """
    blocking = []
    for prereq in prerequisite_nodes:
        if prereq.mastery < threshold:
            blocking.append(prereq.kc_id)
    return blocking


def propagate_gap_upstream(
    student_graph: dict[str, KnowledgeNode],
    failed_kc_id: str,
    depth: int = 3,
) -> list[str]:
    """
    Walk up the DAG from a failed KC to find root cause gaps.
    Returns ordered list of KCs needing remediation (deepest first).
    """
    remediation_path = []
    visited = set()

    def _walk(kc_id: str, current_depth: int):
        if current_depth == 0 or kc_id in visited:
            return
        visited.add(kc_id)
        node = student_graph.get(kc_id)
        if not node:
            return
        for prereq_id in node.prerequisites:
            prereq = student_graph.get(prereq_id)
            if prereq and prereq.mastery < 0.65:
                remediation_path.append(prereq_id)
                _walk(prereq_id, current_depth - 1)

    _walk(failed_kc_id, depth)
    return list(reversed(remediation_path))


# --- Neo4j Cypher queries ---

CYPHER_UPSERT_KC = """
MERGE (kc:KnowledgeComponent {kc_id: $kc_id})
SET kc.name = $name,
    kc.subject = $subject,
    kc.grade_level = $grade_level,
    kc.bloom_level = $bloom_level
RETURN kc
"""

CYPHER_UPSERT_MASTERY = """
MERGE (s:Student {student_id: $student_id})
MERGE (kc:KnowledgeComponent {kc_id: $kc_id})
MERGE (s)-[r:HAS_MASTERY]->(kc)
SET r.mastery = $mastery,
    r.mastery_level = $mastery_level,
    r.attempts = $attempts,
    r.last_updated = datetime()
RETURN r
"""

CYPHER_ADD_PREREQUISITE = """
MATCH (from_kc:KnowledgeComponent {kc_id: $from_kc})
MATCH (to_kc:KnowledgeComponent {kc_id: $to_kc})
MERGE (from_kc)-[r:PREREQUISITE_OF]->(to_kc)
SET r.weight = $weight
RETURN r
"""

CYPHER_GET_STUDENT_GAPS = """
MATCH (s:Student {student_id: $student_id})-[r:HAS_MASTERY]->(kc:KnowledgeComponent)
WHERE r.mastery < $threshold
RETURN kc.kc_id AS kc_id, kc.name AS name, r.mastery AS mastery
ORDER BY r.mastery ASC
"""

CYPHER_GET_PREREQUISITE_CHAIN = """
MATCH path = (start:KnowledgeComponent {kc_id: $kc_id})<-[:PREREQUISITE_OF*1..3]-(prereq)
RETURN prereq.kc_id AS prereq_id, prereq.name AS prereq_name, length(path) AS depth
ORDER BY depth DESC
"""


async def upsert_mastery_neo4j(driver, student_id: str, node: KnowledgeNode):
    """Update mastery in Neo4j graph."""
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        await session.run(
            CYPHER_UPSERT_MASTERY,
            student_id=student_id,
            kc_id=node.kc_id,
            mastery=node.mastery,
            mastery_level=node.mastery_level.value,
            attempts=node.attempts,
        )


async def get_student_gaps(driver, student_id: str, threshold: float = 0.65) -> list[dict]:
    """Get all KCs below mastery threshold for a student."""
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.run(
            CYPHER_GET_STUDENT_GAPS,
            student_id=student_id,
            threshold=threshold,
        )
        return [record.data() async for record in result]


async def get_prerequisite_chain(driver, kc_id: str) -> list[dict]:
    """Get upstream prerequisite chain for a KC."""
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.run(
            CYPHER_GET_PREREQUISITE_CHAIN,
            kc_id=kc_id,
        )
        return [record.data() async for record in result]
