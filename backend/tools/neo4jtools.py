from neomodel import get_config, db, adb
from tools.log import logger
from tools.settings import settings


class Neo4jManager(object):
    def __init__(self):
        self._initialized = False

    def initialize_ogm(self) -> None:
        if not self._initialized:
            config = get_config()
            config.database_url = settings.NEO4J_URL
            db.set_connection(settings.NEO4J_URL)
            adb.set_connection(settings.NEO4J_URL)
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
    try:
        results, meta = await adb.cypher_query("RETURN 1 AS validate")
        if results and results[0][0] == 1:
            logger.info("Successfully confirmed Neo4j instance connectivity via OGM layer!")
            return True
        logger.warning("Neo4j returned unexpected results during health check verification.")
        return False
    except Exception as e:
        logger.exception(f"Neo4j connection validation check failed: {e}")
        return False
