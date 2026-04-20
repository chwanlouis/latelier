from neo4j import AsyncSession

from app.models.ingredient import GeneticFilterResult, PairingScore

# Aldehyde SMILES substrings associated with OR6A2 receptor activation
_OR6A2_ALDEHYDES = {"O=C", "C=O"}


async def compute_pairing_score(
    session: AsyncSession, ingredient_a: str, ingredient_b: str
) -> PairingScore:
    result = await session.run(
        """
        MATCH (a:Ingredient {name: $a})-[:CONTAINS]->(m:Molecule)<-[:CONTAINS]-(b:Ingredient {name: $b})
        RETURN collect(m.name) AS shared_molecules, count(m) AS shared_count
        """,
        a=ingredient_a,
        b=ingredient_b,
    )
    records = await result.data()
    shared = records[0]["shared_molecules"] if records else []
    count = records[0]["shared_count"] if records else 0

    # Simple scoring: shared molecules / total unique molecules of ingredient_a
    total_result = await session.run(
        "MATCH (a:Ingredient {name: $a})-[:CONTAINS]->(m:Molecule) RETURN count(m) AS total",
        a=ingredient_a,
    )
    total_data = await total_result.data()
    total = total_data[0]["total"] if total_data else 1

    score = round(count / total, 4)
    soap_risk = any(_has_aldehyde(m) for m in shared)
    return PairingScore(
        ingredient_a=ingredient_a,
        ingredient_b=ingredient_b,
        score=score,
        shared_molecules=shared,
        soap_risk=soap_risk,
    )


async def genetic_filter(session: AsyncSession, ingredient: str) -> GeneticFilterResult:
    result = await session.run(
        """
        MATCH (i:Ingredient {name: $name})-[:CONTAINS]->(m:Molecule)
        WHERE m.smiles IS NOT NULL
        RETURN m.name AS mol_name, m.smiles AS smiles
        """,
        name=ingredient,
    )
    records = await result.data()
    aldehyde_molecules = [
        r["mol_name"] for r in records if r["smiles"] and _has_aldehyde(r["smiles"])
    ]
    return GeneticFilterResult(
        ingredient=ingredient,
        has_or6a2_risk=len(aldehyde_molecules) > 0,
        aldehyde_molecules=aldehyde_molecules,
    )


def _has_aldehyde(smiles: str) -> bool:
    return any(marker in smiles for marker in _OR6A2_ALDEHYDES)
