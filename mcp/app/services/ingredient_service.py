from neo4j import AsyncSession

from app.models.ingredient import Ingredient, Molecule


async def list_ingredients(session: AsyncSession, skip: int = 0, limit: int = 20) -> list[Ingredient]:
    result = await session.run(
        """
        MATCH (i:Ingredient)
        OPTIONAL MATCH (i)-[:CONTAINS]->(m:Molecule)
        RETURN i, collect(m) AS molecules
        SKIP $skip LIMIT $limit
        """,
        skip=skip,
        limit=limit,
    )
    records = await result.data()
    return [_map_ingredient(r) for r in records]


async def fetch_ingredient(session: AsyncSession, ingredient_id: str) -> Ingredient | None:
    result = await session.run(
        """
        MATCH (i:Ingredient {id: $id})
        OPTIONAL MATCH (i)-[:CONTAINS]->(m:Molecule)
        RETURN i, collect(m) AS molecules
        """,
        id=ingredient_id,
    )
    records = await result.data()
    return _map_ingredient(records[0]) if records else None


async def search_ingredients_by_molecule(session: AsyncSession, smiles: str) -> list[Ingredient]:
    result = await session.run(
        """
        MATCH (m:Molecule {smiles: $smiles})<-[:CONTAINS]-(i:Ingredient)
        OPTIONAL MATCH (i)-[:CONTAINS]->(mol:Molecule)
        RETURN i, collect(mol) AS molecules
        """,
        smiles=smiles,
    )
    records = await result.data()
    return [_map_ingredient(r) for r in records]


def _map_ingredient(record: dict) -> Ingredient:
    node = record["i"]
    molecules = [
        Molecule(
            id=m.get("id", ""),
            name=m.get("name", ""),
            smiles=m.get("smiles", ""),
            cas_number=m.get("cas_number"),
            flavor_profile=m.get("flavor_profile"),
        )
        for m in record.get("molecules", [])
        if m
    ]
    return Ingredient(
        id=node.get("id", ""),
        name=node.get("name", ""),
        category=node.get("category"),
        molecules=molecules,
    )
