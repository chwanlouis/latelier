import ijson
from typing import Any
from pathlib import Path
from tools.log import logger
from repository.neo4j.compound import compound_repository


def parse_float_safely(val: Any) -> float | None:
    """Safely handles cast conversions for physical property fields."""
    if val is None or str(val).strip().lower() in ("null", "", "none"):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

async def bulk_ingest_compounds(file_path: str, batch_size: int = 5000):
    """
    Streams the massive compounds.json dataset via memory-efficient ijson sequential chunking
    and bulk-upserts entities asynchronously using the transaction-guarded CompoundRepository singleton.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Compounds source catalog missing at target: {path}")
        return

    batch_buffer = []
    total_ingested = 0

    logger.info(f"Starting memory-optimized compound matrix ingestion from: {file_path}")

    with open(path, 'rb') as f:
        # Stream array items sequentially without reading the full file into system memory
        for item in ijson.items(f, '', multiple_values=True):
            if not item.get("id") or not item.get("public_id"):
                continue

            # Structure payload matrix to map raw JSON fields precisely to your OGM node properties
            props = {
                "foodb_id": int(item["id"]),
                "compound_id": item["public_id"].strip(),
                "name": item["name"].strip() if item.get("name") else "Unknown Compound",
                "state": item.get("state"),
                "annotation_quality": item.get("annotation_quality"),
                "description": item.get("description"),
                "cas_number": item.get("cas_number"),
                "smiles": item.get("moldb_smiles"),
                "inchi": item.get("moldb_inchi"),
                "inchikey": item.get("moldb_inchikey"),
                "iupac_name": item.get("moldb_iupac"),
                "mono_mass": parse_float_safely(item.get("moldb_mono_mass")),
                "kingdom": item.get("kingdom"),
                "superklass": item.get("superklass"),
                "klass": item.get("klass"),
                "subklass": item.get("subklass"),
            }
            batch_buffer.append(props)

            if len(batch_buffer) >= batch_size:
                # Use the clean singleton engine abstraction
                await compound_repository.bulk_upsert(batch_buffer)
                total_ingested += len(batch_buffer)
                logger.info(f"Ingested {total_ingested} Compound nodes via transaction registry.")
                batch_buffer = []

        # Flush any trailing residual objects remaining in the buffer
        if batch_buffer:
            await compound_repository.bulk_upsert(batch_buffer)
            total_ingested += len(batch_buffer)
            logger.info(f"Flushed final {len(batch_buffer)} Compound nodes to Neo4j database matrix.")

    logger.info(f"Compound node pipeline execution finished cleanly. Global structures built: {total_ingested}")