from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from module.knowledge_graph.pipelines.flavor_loader import bulk_ingest_flavors
from module.knowledge_graph.pipelines.enzyme_loader import bulk_ingest_enzymes
from module.knowledge_graph.pipelines.food_loader import bulk_ingest_foods
from module.knowledge_graph.pipelines.nutrient_loader import bulk_ingest_nutrients
from module.knowledge_graph.pipelines.compound_loader import bulk_ingest_compounds
from module.knowledge_graph.pipelines.food_composition_rel_loader import ingest_relationships as ingest_food_edges
from module.knowledge_graph.pipelines.compound_enzyme_rel_loader import ingest_compound_enzyme_relationships
from module.knowledge_graph.pipelines.compound_flavor_rel_loader import ingest_compound_flavor_relationships


foodb_router = APIRouter(
    prefix="/foodb",
    tags=["FooDB Pipeline Engine"]
)


class PipelineSelector(BaseModel):
    flavors: bool = True
    enzymes: bool = True
    foods: bool = True
    nutrients: bool = True
    compounds: bool = True
    food_edges: bool = True
    compound_enzymes: bool = True
    compound_flavors: bool = True


class PipelineRequest(BaseModel):
    data_dir: str = "data/foodb"
    selectors: PipelineSelector = Field(default_factory=PipelineSelector)


async def execute_orchestrated_pipeline(base_path: Path, selectors: PipelineSelector):
    if selectors.flavors:
        await bulk_ingest_flavors(str(base_path / "Flavor.json"))
    if selectors.enzymes:
        await bulk_ingest_enzymes(str(base_path / "Enzyme.json"))
    if selectors.foods:
        await bulk_ingest_foods(str(base_path / "Food.json"))
    if selectors.nutrients:
        await bulk_ingest_nutrients(str(base_path / "Nutrient.json"))
    if selectors.compounds:
        await bulk_ingest_compounds(str(base_path / "Compound.json"))
    if selectors.food_edges:
        await ingest_food_edges(str(base_path / "Content.json"))
    if selectors.compound_enzymes:
        await ingest_compound_enzyme_relationships(str(base_path / "CompoundsEnzyme.json"))
    if selectors.compound_flavors:
        await ingest_compound_flavor_relationships(str(base_path / "CompoundsFlavor.json"))


@foodb_router.post("/runPipeline", status_code=status.HTTP_202_ACCEPTED)
async def run_foodb_pipeline(payload: PipelineRequest, background_tasks: BackgroundTasks):
    base_path = Path(payload.data_dir)

    if not base_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution stopped. Base catalog directory missing: {base_path}"
        )

    background_tasks.add_task(execute_orchestrated_pipeline, base_path, payload.selectors)

    return {
        "status": "ACCEPTED",
        "message": "FooDB knowledge graph ingestion strategy started in the background.",
        "target_directory": str(base_path)
    }
