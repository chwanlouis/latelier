from neo4j import AsyncSession

from app.models.ingredient import Molecule


async def list_molecules(session: AsyncSession, skip: int = 0, limit: int = 20) -> list[Molecule]:
    result = await session.run(
        "MATCH (m:Molecule) RETURN m SKIP $skip LIMIT $limit",
        skip=skip,
        limit=limit,
    )
    records = await result.data()
    return [_map_molecule(r["m"]) for r in records]


async def fetch_molecule(session: AsyncSession, molecule_id: str) -> Molecule | None:
    result = await session.run(
        "MATCH (m:Molecule {id: $id}) RETURN m",
        id=molecule_id,
    )
    records = await result.data()
    return _map_molecule(records[0]["m"]) if records else None


def _map_molecule(node: dict) -> Molecule:
    return Molecule(
        id=node.get("id", ""),
        name=node.get("name", ""),
        smiles=node.get("smiles", ""),
        cas_number=node.get("cas_number"),
        flavor_profile=node.get("flavor_profile"),
    )
