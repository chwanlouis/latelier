from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.neo4j import get_session
from app.models.ingredient import Molecule
from app.services.molecule_service import fetch_molecule, list_molecules

router = APIRouter(prefix="/molecules", tags=["molecules"])

CurrentUser = Annotated[dict, Depends(get_current_user)]
Neo4jSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[Molecule])
async def get_molecules(
    session: Neo4jSession,
    _: CurrentUser,
    skip: int = 0,
    limit: int = 20,
):
    return await list_molecules(session, skip=skip, limit=limit)


@router.get("/{molecule_id}", response_model=Molecule)
async def get_molecule(
    molecule_id: str,
    session: Neo4jSession,
    _: CurrentUser,
):
    molecule = await fetch_molecule(session, molecule_id)
    if molecule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Molecule not found")
    return molecule
