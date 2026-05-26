import ijson
import asyncio
from pathlib import Path
from datetime import datetime
from tools.log import logger
from repository.neo4j.enzyme import enzyme_repository

def parse_iso_date(date_str: str) -> datetime | None:
    """Safely handles FooDB string timestamp conversions into native datetimes."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        return None

async def bulk_ingest_enzymes(file_path: str, batch_size: int = 5000):
    """
    Streams enzymes.json iteratively using ijson and offloads high-speed,
    transaction-guarded upsert operations onto the EnzymeRepository singleton.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Enzymes source catalog missing at target path: {path}")
        return

    batch_buffer = []
    total_nodes_processed = 0

    logger.info(f"Initiating streaming Enzyme node ingestion sequence from: {file_path}")

    with open(path, 'rb') as f:
        # Handles standard JSON lists of objects sequentially via stream
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("id") or not item.get("name"):
                continue

            # Deterministically pad enzyme structural IDs matching your catalog logic
            foodb_id_int = int(item["id"])
            generated_public_id = item.get("public_id") or f"FDBE{str(foodb_id_int).zfill(6)}"

            # Structure payload matrix to map raw JSON fields precisely to your OGM node properties
            transformed_enzyme = {
                "foodb_id": foodb_id_int,
                "enzyme_id": generated_public_id.strip(),
                "name": item["name"].strip(),
                "gene_name": item.get("gene_name"),
                "description": item.get("description"),
                "go_classification": item.get("go_classification"),
                "general_function": item.get("general_function"),
                "specific_function": item.get("specific_function"),
                "pathway": item.get("pathway"),
                "reaction": item.get("reaction"),
                "cellular_location": item.get("cellular_location"),
                "uniprot_name": item.get("uniprot_name"),
                "uniprot_id": item.get("uniprot_id"),
                "created_at": parse_iso_date(item.get("created_at")),
                "updated_at": parse_iso_date(item.get("updated_at"))
            }
            batch_buffer.append(transformed_enzyme)

            if len(batch_buffer) >= batch_size:
                # Delegate transaction block to your pre-configured singleton instance
                await enzyme_repository.bulk_upsert(batch_buffer)
                total_nodes_processed += len(batch_buffer)
                logger.info(f"Ingested {total_nodes_processed} Enzyme nodes via transaction registry.")
                batch_buffer = []  # Clear memory footprint

        # Flush trailing records left over at the bottom of the file
        if batch_buffer:
            await enzyme_repository.bulk_upsert(batch_buffer)
            total_nodes_processed += len(batch_buffer)
            logger.info(f"Flushed final {len(batch_buffer)} Enzyme nodes to Neo4j database matrix.")

    logger.info(f"Enzyme lifecycle complete. Total nodes securely stored/updated: {total_nodes_processed}")