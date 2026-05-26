import ijson
from pathlib import Path
from datetime import datetime
from tools.log import logger
from repository.neo4j.compound_flavor import compound_flavor_repository


def parse_iso_date(date_str: str) -> datetime | None:
    """Safely converts FooDB string timestamps into native Python datetime objects."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        return None

async def ingest_compound_flavor_relationships(file_path: str, batch_size: int = 5000):
    """
    Streams CompoundFlavor.json sequentially using memory-efficient ijson streaming
    and delegates bulk edge loading tasks to the CompoundFlavorRepository singleton.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Mapping source data table missing at target path: {path}")
        return

    batch_buffer = []
    total_edges_wired = 0

    logger.info(f"Beginning dynamic Compound <-> Flavor binding pipeline from: {file_path}")

    with open(path, 'rb') as f:
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("compound_id") or not item.get("flavor_id"):
                continue

            # Map fields safely. Ensure "source_id" and "target_id" are mapped explicitly
            # to feed your validated Repository Base MATCH clause.
            edge_payload = {
                "source_id": int(item["compound_id"]), # Bound to matching (src:Compound)
                "target_id": int(item["flavor_id"]),   # Bound to matching (tgt:Flavor)
                "foodb_id": int(item["id"]),
                "source_node_id": int(item["source_id"]) if item.get("source_id") else None,
                "source_node_type": item.get("source_type") or "Compound",
                "source_type": item.get("citations") or "UNKNOWN",
                "created_at": parse_iso_date(item.get("created_at")),
                "updated_at": parse_iso_date(item.get("updated_at"))
            }
            batch_buffer.append(edge_payload)

            if len(batch_buffer) >= batch_size:
                # High-speed non-blocking async execution using adb under the hood
                await compound_flavor_repository.bulk_link(batch_buffer)
                total_edges_wired += len(batch_buffer)
                logger.info(f"Wired {total_edges_wired} flavor profiles: (:Compound)-[:HAS_FLAVOR]->(:Flavor)")
                batch_buffer = []

        # Flush trailing leftover elements inside the memory buffer
        if batch_buffer:
            await compound_flavor_repository.bulk_link(batch_buffer)
            total_edges_wired += len(batch_buffer)

    logger.info(f"Compound-Flavor matrix complete! Total edge properties synced: {total_edges_wired}")