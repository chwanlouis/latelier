from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.neo4j import get_session
from app.models.ingredient import Ingredient
from app.services.ingredient_service import (
    fetch_ingredient,
    list_ingredients,
    search_ingredients_by_molecule,
)

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

CurrentUser = Annotated[dict, Depends(get_current_user)]
Neo4jSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[Ingredient])
async def get_ingredients(
    session: Neo4jSession,
    _: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    return await list_ingredients(session, skip=skip, limit=limit)


@router.get("/{ingredient_id}", response_model=Ingredient)
async def get_ingredient(
    ingredient_id: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    ingredient = await fetch_ingredient(session, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return ingredient


@router.get("/search/by-molecule", response_model=list[Ingredient])
async def search_by_molecule(
    smiles: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    return await search_ingredients_by_molecule(session, smiles)
