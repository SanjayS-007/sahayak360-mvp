"""
Neo4j async driver management.
"""

from neo4j import AsyncGraphDatabase

from config import settings


_driver = None


async def get_neo4j_driver():
    """Get or create Neo4j async driver singleton."""
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            database=settings.NEO4J_DATABASE,
        )
    return _driver


async def close_neo4j():
    """Close driver on shutdown."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def verify_neo4j_connectivity():
    """Verify Neo4j is reachable."""
    driver = await get_neo4j_driver()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.run("RETURN 1 AS ok")
        record = await result.single()
        return record["ok"] == 1


async def init_neo4j_schema():
    """Create indexes and constraints on first run."""
    driver = await get_neo4j_driver()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        # Constraints
        await session.run(
            "CREATE CONSTRAINT student_id IF NOT EXISTS "
            "FOR (s:Student) REQUIRE s.student_id IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT kc_id IF NOT EXISTS "
            "FOR (kc:KnowledgeComponent) REQUIRE kc.kc_id IS UNIQUE"
        )
        # Indexes
        await session.run(
            "CREATE INDEX kc_subject IF NOT EXISTS "
            "FOR (kc:KnowledgeComponent) ON (kc.subject)"
        )
        await session.run(
            "CREATE INDEX kc_grade IF NOT EXISTS "
            "FOR (kc:KnowledgeComponent) ON (kc.grade_level)"
        )
