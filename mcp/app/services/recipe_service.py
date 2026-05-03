from neo4j import AsyncSession

from app.models.ingredient import DishPreference, PreferenceRecommendation, Recipe, Technique


async def search_recipes_by_preference(
    session: AsyncSession, preference: DishPreference, limit: int = 10
) -> PreferenceRecommendation:
    """Return recipes that match a technique+ingredient preference."""
    result = await session.run(
        """
        MATCH (r:Recipe)-[:USES_TECHNIQUE]->(t:Technique)
        WHERE toLower(t.name) CONTAINS toLower($technique)
        OPTIONAL MATCH (r)-[:CONTAINS]->(i:Ingredient)
        WHERE toLower(i.name) CONTAINS toLower($ingredient)
        WITH r, collect(DISTINCT t) AS techniques, count(DISTINCT i) AS ingredient_matches
        ORDER BY ingredient_matches DESC
        LIMIT $limit
        OPTIONAL MATCH (r)-[:USES_TECHNIQUE]->(all_t:Technique)
        RETURN r, collect(DISTINCT all_t) AS all_techniques
        """,
        technique=preference.technique,
        ingredient=preference.ingredient,
        limit=limit,
    )
    records = await result.data()
    recipes = [_map_recipe(rec) for rec in records]
    return PreferenceRecommendation(preference=preference, recipes=recipes)


async def get_recipe(session: AsyncSession, recipe_id: str) -> Recipe | None:
    """Fetch a single recipe by id."""
    result = await session.run(
        """
        MATCH (r:Recipe {id: $id})
        OPTIONAL MATCH (r)-[:USES_TECHNIQUE]->(t:Technique)
        RETURN r, collect(t) AS techniques
        """,
        id=recipe_id,
    )
    records = await result.data()
    return _map_recipe(records[0]) if records else None


async def list_recipes(
    session: AsyncSession, skip: int = 0, limit: int = 20
) -> list[Recipe]:
    """List recipes with pagination."""
    result = await session.run(
        """
        MATCH (r:Recipe)
        OPTIONAL MATCH (r)-[:USES_TECHNIQUE]->(t:Technique)
        RETURN r, collect(t) AS techniques
        SKIP $skip LIMIT $limit
        """,
        skip=skip,
        limit=limit,
    )
    records = await result.data()
    return [_map_recipe(rec) for rec in records]


def _map_recipe(record: dict) -> Recipe:
    node = record["r"]
    techniques = [
        Technique(name=t.get("name", ""), type=t.get("type", ""))
        for t in record.get("techniques", []) or record.get("all_techniques", [])
        if t
    ]
    return Recipe(
        id=node.get("id", ""),
        title=node.get("title", ""),
        instructions=node.get("instructions", ""),
        techniques=techniques or None,
    )
