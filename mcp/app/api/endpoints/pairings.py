from typing import Annotated

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.neo4j import get_session
from app.models.ingredient import GeneticFilterResult, PairingScore
from app.services.pairing_service import compute_pairing_score, genetic_filter

router = APIRouter(prefix="/pairings", tags=["pairings"])

CurrentUser = Annotated[dict, Depends(get_current_user)]
Neo4jSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/score", response_model=PairingScore)
async def pairing_score(
    ingredient_a: str,
    ingredient_b: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    return await compute_pairing_score(session, ingredient_a, ingredient_b)


@router.get("/genetic-filter", response_model=GeneticFilterResult)
async def or6a2_filter(
    ingredient: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    return await genetic_filter(session, ingredient)
