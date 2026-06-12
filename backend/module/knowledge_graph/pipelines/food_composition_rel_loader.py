import ijson
from pathlib import Path
from module.core.tools.log import logger
from module.knowledge_graph.repository.neo4j.food_nutrient import food_nutrient_repository
from module.knowledge_graph.repository.neo4j.food_compound import food_compound_repository


def parse_float_safely(val: any, default: float = 0.0) -> float:
    """Safely handles conversion for values that might contain corrupted string formatting."""
    if val is None or str(val).strip().lower() in ("null", "", "none"):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


async def ingest_relationships(file_path: str, batch_size: int = 5000):
    """
    Streams the unified food compositions data lake table sequentially using ijson,
    sorting records at runtime into high-speed async repository batches.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Source data table missing at target: {path}")
        return

    nutrient_batch = []
    compound_batch = []

    total_nutrients = 0
    total_compounds = 0

    logger.info(f"Beginning unified edge mapping sequence from: {file_path}")

    with open(path, 'rb') as f:
        for item in ijson.items(f, '', multiple_values=True):
            source_type = item.get("source_type")
            if not source_type or not item.get("food_id") or not item.get("source_id"):
                continue

            # Core payload layout for parent properties matching the MATCH criteria
            # 'source_id' maps to the source node, 'target_id' maps to the destination node inside Base
            base_edge = {
                "source_id": int(item["food_id"]),
                "target_id": int(item["source_id"]),
                "unit": item.get("orig_unit") or "mg",
                "source_type": item.get("citation") or "UNKNOWN",
                "preparation_type": item.get("preparation_type") or "raw"
            }

            if source_type == "Nutrient":
                base_edge["value"] = parse_float_safely(item.get("standard_content"))
                nutrient_batch.append(base_edge)

            elif source_type == "Compound":
                base_edge["min_concentration"] = parse_float_safely(item.get("orig_min"))
                base_edge["max_concentration"] = parse_float_safely(item.get("orig_max"))
                compound_batch.append(base_edge)

            # Check individual threshold ceilings dynamically
            if len(nutrient_batch) >= batch_size:
                await food_nutrient_repository.bulk_link(nutrient_batch)
                total_nutrients += len(nutrient_batch)
                logger.info(f"Linked {total_nutrients} (:Food)-[:HAS_NUTRIENT]->(:Nutrient)")
                nutrient_batch = []

            if len(compound_batch) >= batch_size:
                await food_compound_repository.bulk_link(compound_batch)
                total_compounds += len(compound_batch)
                logger.info(f"Linked {total_compounds} (:Food)-[:CONTAINS_COMPOUND]->(:Compound)")
                compound_batch = []

        # Flush residual data blocks at the tail end of the file stream
        if nutrient_batch:
            await food_nutrient_repository.bulk_link(nutrient_batch)
            total_nutrients += len(nutrient_batch)

        if compound_batch:
            await food_compound_repository.bulk_link(compound_batch)
            total_compounds += len(compound_batch)

    logger.info(
        f"Relationship build finished! Nutrients mapped: {total_nutrients}, Compounds mapped: {total_compounds}"
    )