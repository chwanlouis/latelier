import ijson
import asyncio
from datetime import datetime
from tools.log import logger
from repository.neo4j.food import food_repository


def parse_iso_date(date_str: str) -> datetime:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        return None


async def bulk_ingest_foods(file_path: str, batch_size: int = 1000):
    logger.info(f"Initiating Food entity node injection sequence from NDJSON: {file_path}")
    batch_buffer = []
    total_nodes_created = 0

    try:
        with open(file_path, 'rb') as f:
            # Streams separate top-level JSON objects iteratively using multiple_values=True
            for item in ijson.items(f, '', multiple_values=True):
                if not item.get("id") or not item.get("name"):
                    continue

                transformed_food = {
                    "food_id": str(item["id"]),
                    "name": item["name"],
                    "name_scientific": item.get("scientific_name"),

                    # Handles future name changes or source aliases safely (extracts list or defaults to empty)
                    "aliases": item.get("aliases", []),

                    "description": item.get("description"),
                    "food_group": item.get("food_group"),
                    "food_subgroup": item.get("food_subgroup"),
                    "created_at": parse_iso_date(item.get("created_at")),
                    "updated_at": parse_iso_date(item.get("updated_at"))
                }
                batch_buffer.append(transformed_food)

                # Flush chunk buffer to the database when target batch threshold is met
                if len(batch_buffer) >= batch_size:
                    # Pipeline delegates writing boundaries completely to the repo layer
                    await food_repository.bulk_upsert(batch_buffer)
                    total_nodes_created += len(batch_buffer)
                    logger.info(f"Committed {total_nodes_created} primary Food nodes...")
                    batch_buffer = []  # Clear RAM footprint

            # Process any remaining records left over at the bottom of the file stream
            if batch_buffer:
                await food_repository.bulk_upsert(batch_buffer)
                total_nodes_created += len(batch_buffer)

        logger.info(f"Ingestion lifecycle successful. Total Food nodes safely stored: {total_nodes_created}")

    except Exception as e:
        logger.error(f"Critical system failure during Food data ingestion loop: {e}")
        raise e


if __name__ == "__main__":
    # Target path pointing to your raw unpacked FooDB JSON mirror dump directory
    file_path = "..\\data\\foodb\\foodb_2020_04_07_json\\food.json"

    # Run the streaming pipeline
    asyncio.run(ingest_food_json_file(file_path, batch_size=1000))