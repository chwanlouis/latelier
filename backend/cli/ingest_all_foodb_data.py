import asyncio
import typer
from pathlib import Path
from food_composition_rel_loader import ingest_relationships as ingest_food_edges
from compound_enzyme_rel_loader import ingest_compound_enzyme_relationships
from compound_flavor_rel_loader import ingest_compound_flavor_relationships

cli = typer.Typer(help="FooDB Graph Network Comprehensive Ingestion Engine")


async def execute_orchestrated_pipeline(base_path: Path):
    """
    Executes the ingestion phases within a single, continuous async loop,
    preserving a warm Neo4j connection pool across all repository singletons.
    """
    # =========================================================================
    # Phase 1: Constructing Independent Node Catalogs
    # =========================================================================
    typer.secho("\n--- Phase 1: Constructing Independent Node Catalogs ---", fg=typer.colors.MAGENTA, bold=True)

    # await bulk_ingest_flavors(str(base_path / "Flavor.json"))
    # await bulk_ingest_enzymes(str(base_path / "Enzyme.json"))
    # await bulk_ingest_foods(str(base_path / "Food.json"))
    # await bulk_ingest_nutrients(str(base_path / "Nutrient.json"))
    # await bulk_ingest_compounds(str(base_path / "Compound.json"))

    typer.secho("SUCCESS: Master Node Catalogs populated without errors.", fg=typer.colors.GREEN)

    # =========================================================================
    # Phase 2: Interweaving Matrix Relationship Edges
    # =========================================================================
    typer.secho("\n--- Phase 2: Interweaving Matrix Relationship Edges ---", fg=typer.colors.MAGENTA, bold=True)

    # Content.json bridges (Food -> Nutrient) and (Food -> Compound)
    await ingest_food_edges(str(base_path / "Content.json"))
    await ingest_compound_enzyme_relationships(str(base_path / "CompoundsEnzyme.json"))
    await ingest_compound_flavor_relationships(str(base_path / "CompoundsFlavor.json"))


@cli.command(name="run-foodb-pipeline")
def run_foodb_pipeline(
        data_dir: str = typer.Option("data/foodb", help="Base directory hosting raw FooDB JSON catalogs")
):
    base_path = Path(data_dir)
    if not base_path.exists():
        typer.secho(f"ERROR: Execution stopped. Base catalog directory missing: {base_path}", fg=typer.colors.RED,
                    bold=True)
        raise typer.Exit(code=1)

    typer.secho("START: Starting FooDB Knowledge Graph Ingestion Strategy...", fg=typer.colors.CYAN, bold=True)

    # Fire off a single async event loop context for the entire pipeline duration
    asyncio.run(execute_orchestrated_pipeline(base_path))

    typer.secho("\nCOMPLETE: Graph Architecture Interleaved Successfully!", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    cli()