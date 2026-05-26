import ijson
import asyncio
from pathlib import Path
from datetime import datetime
from tools.log import logger
from repository.neo4j.nutrient import nutrient_repository

def parse_datetime(dt_str: str) -> datetime | None:
    """Safely handles FooDB ISO format timestamp conversions into native datetimes."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", ""))
    except ValueError:
        return None

def parse_bool_safely(val: any) -> bool:
    """Standardizes dynamic truthiness checks for incoming nutrient schema flags."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")

async def bulk_ingest_nutrients(file_path: str, batch_size: int = 5000):
    """
    Streams the nutrients.json dataset iteratively using ijson and offloads
    high-speed batch transaction writes onto the NutrientRepository singleton.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Nutrients source catalog missing at target: {path}")
        return

    batch_buffer = []
    total_ingested = 0

    logger.info(f"Starting memory-optimized nutrient node ingestion matrix from: {file_path}")

    with open(path, 'rb') as f:
        # Sequentially scan JSON list structures elements with zero memory overhead
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("id") or not item.get("public_id"):
                continue

            # Map raw dictionary streams strictly to your Nutrient OGM property definitions
            props = {
                "foodb_id": int(item["id"]),
                "nutrient_id": item["public_id"].strip(),
                "name": item["name"].strip() if item.get("name") else "Unknown Nutrient",
                "legacy_id": item.get("legacy_id"),
                "export": parse_bool_safely(item.get("export")),
                "state": item.get("state"),
                "annotation_quality": item.get("annotation_quality"),
                "description": item.get("description"),
                "wikipedia_id": item.get("wikipedia_id"),
                "comments": item.get("comments"),
                "dfc_id": item.get("dfc_id"),
                "duke_id": item.get("duke_id"),
                "eafus_id": item.get("eafus_id"),
                "dfc_name": item.get("dfc_name"),
                "compound_source": item.get("compound_source"),
                "metabolism": item.get("metabolism"),
                "synthesis_citations": item.get("synthesis_citations"),
                "general_citations": item.get("general_citations"),
                "creator_id": item.get("creator_id"),
                "updater_id": item.get("updater_id"),
                "created_at": parse_datetime(item.get("created_at")),
                "updated_at": parse_datetime(item.get("updated_at")),
            }
            batch_buffer.append(props)

            if len(batch_buffer) >= batch_size:
                # Direct delegator write to your unified singleton architecture
                await nutrient_repository.bulk_upsert(batch_buffer)
                total_ingested += len(batch_buffer)
                logger.info(f"Ingested {total_ingested} Nutrient nodes via transaction registry.")
                batch_buffer = []  # Clear memory reference pointer

        # Flush any trailing residual elements resting at the bottom of the file stream
        if batch_buffer:
            await nutrient_repository.bulk_upsert(batch_buffer)
            total_ingested += len(batch_buffer)
            logger.info(f"Flushed final {len(batch_buffer)} Nutrient nodes to Neo4j database matrix.")

    logger.info(f"Nutrient node pipeline execution finished cleanly. Global structures built: {total_ingested}")