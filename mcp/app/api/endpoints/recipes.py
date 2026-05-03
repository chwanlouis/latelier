from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.neo4j import get_session
from app.models.ingredient import DishPreference, PreferenceRecommendation, Recipe
from app.services.recipe_service import get_recipe, list_recipes, search_recipes_by_preference

router = APIRouter(prefix="/recipes", tags=["recipes"])

CurrentUser = Annotated[dict, Depends(get_current_user)]
Neo4jSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[Recipe])
async def get_recipes(
    session: Neo4jSession,
    _: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    return await list_recipes(session, skip=skip, limit=limit)


@router.get("/recommendations/by-preference", response_model=PreferenceRecommendation)
async def recommend_by_preference(
    technique: str,
    ingredient: str,
    session: Neo4jSession,
    _: CurrentUser,
    limit: int = 10,
):
    """Return recipes matching a technique+ingredient preference (e.g. technique=Grilling, ingredient=steak)."""
    preference = DishPreference(technique=technique, ingredient=ingredient)
    return await search_recipes_by_preference(session, preference, limit=limit)


@router.get("/{recipe_id}", response_model=Recipe)
async def read_recipe(
    recipe_id: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    recipe = await get_recipe(session, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe
