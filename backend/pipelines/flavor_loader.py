import ijson
from pathlib import Path
from datetime import datetime
from tools.log import logger
from repository.neo4j.flavor import flavor_repository


def parse_iso_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        return None


async def bulk_ingest_flavors(file_path: str, batch_size: int = 5000):
    """
    Streams raw flavors.json sequentially using low-memory ijson streaming
    and offloads high-speed batch transactions onto the FlavorRepository.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Flavor data file catalog missing at target path: {path}")
        return

    batch_buffer = []
    total_ingested = 0

    logger.info(f"Streaming flavor configurations from data source: {file_path}")

    with open(path, 'rb') as f:
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("id") or not item.get("name"):
                continue

            # Keep dictionary keys perfectly aligned with your Flavor model properties
            batch_buffer.append({
                "foodb_id": int(item["id"]),
                "name": item["name"].strip().lower(),
                "flavor_group": item.get("flavor_group"),
                "category": item.get("category"),
                "created_at": parse_iso_date(item.get("created_at")),
                "updated_at": parse_iso_date(item.get("updated_at"))
            })

            if len(batch_buffer) >= batch_size:
                # Cleaner execution abstraction using your architecture!
                await flavor_repository.bulk_upsert(batch_buffer)
                total_ingested += len(batch_buffer)
                logger.info(f"Batched {total_ingested} nodes to FlavorRepository.")
                batch_buffer = []

        # Handle residual items left in buffer
        if batch_buffer:
            await flavor_repository.bulk_upsert(batch_buffer)
            total_ingested += len(batch_buffer)

    logger.info(f"Flavor Node catalog ingestion completed cleanly. Total nodes structured: {total_ingested}")