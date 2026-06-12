import ijson
from pathlib import Path
from datetime import datetime
from module.core.tools.log import logger
from module.knowledge_graph.repository.neo4j.compound_enzyme import compound_enzyme_repository


def parse_iso_date(date_str: str) -> datetime | None:
    """Safely converts FooDB string timestamps into native Python datetime objects."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        return None


async def ingest_compound_enzyme_relationships(file_path: str, batch_size: int = 5000):
    """
    Streams compounds_enzymes.json utilizing memory-efficient sequential ijson chunking
    and bulk-links Compound nodes to Enzyme nodes via the unified CompoundEnzymeRepository singleton.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Mapping source data table missing at target path: {path}")
        return

    batch_buffer = []
    total_edges_wired = 0

    logger.info(f"Beginning dynamic Enzyme <-> Compound binding pipeline from: {file_path}")

    with open(path, 'rb') as f:
        # Handles raw data stream continuously without expanding the array into RAM
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("compound_id") or not item.get("enzyme_id"):
                continue

            # Structure payload matrix to map raw JSON fields precisely to your OGM edge properties
            # Ensure "source_id" and "target_id" are mapped explicitly to feed your Repository Base MATCH clause
            edge_payload = {
                "source_id": int(item["compound_id"]),  # Bound to matching (src:Compound)
                "target_id": int(item["enzyme_id"]),    # Bound to matching (tgt:Enzyme)
                "foodb_id": int(item["id"]),
                "unit": "unitless",
                "preparation_type": "raw",
                "source_type": item.get("citations") or "UNKNOWN",
                "created_at": parse_iso_date(item.get("created_at")),
                "updated_at": parse_iso_date(item.get("updated_at"))
            }
            batch_buffer.append(edge_payload)

            if len(batch_buffer) >= batch_size:
                # High-speed non-blocking async bulk link execution
                await compound_enzyme_repository.bulk_link(batch_buffer)
                total_edges_wired += len(batch_buffer)
                logger.info(f"Wired {total_edges_wired} metabolic paths: (:Compound)-[:INTERACTS_WITH_ENZYME]->(:Enzyme)")
                batch_buffer = []

        # Flush any remaining items in the buffer
        if batch_buffer:
            await compound_enzyme_repository.bulk_link(batch_buffer)
            total_edges_wired += len(batch_buffer)

    logger.info(f"Enzyme-Compound matrix complete! Total edge properties synced: {total_edges_wired}")