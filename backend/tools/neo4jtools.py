from neomodel import get_config, db, adb
from tools.log import logger
from tools.settings import settings


class Neo4jManager(object):
    def __init__(self):
        self._initialized = False

    def initialize_ogm(self) -> None:
        if not self._initialized:
            config = get_config()
            config.database_url = settings.NEO4J_URI
            db.set_connection(settings.NEO4J_URI)
            adb.set_connection(settings.NEO4J_URI)
            self._initialized = True
            logger.info("Neomodel OGM engine initialized successfully.")

    @property
    def driver(self):
        if not self._initialized:
            self.initialize_ogm()
        return db.driver


neo4j_manager = Neo4jManager()
neo4j_manager.initialize_ogm()


async def test_neo4j_connection() -> bool:
    """
    Validates live database connectivity by executing a lightweight Cypher query.
    Returns True if the connection is active, False otherwise.
    """
    try:
        # 1. Resolve the coroutine to enter the async context manager
        results, meta = await adb.cypher_query("RETURN 1 AS validate")

        if results and results[0][0] == 1:
            logger.info("Successfully confirmed Neo4j instance connectivity via OGM layer!")
            return True

        # If we exit the block without returning True, something went wrong
        logger.warning("Neo4j returned unexpected results during health check verification.")
        return False

    except Exception as e:
        logger.exception(f"Neo4j connection validation check failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    logger.info("Running standalone database connectivity diagnostics...")
    success = asyncio.run(test_neo4j_connection())
    if success:
        logger.info("Diagnostics PASSED. Infrastructure is healthy.")
    else:
        logger.critical("Diagnostics FAILED. Verify Neo4j instance state and network routes.")