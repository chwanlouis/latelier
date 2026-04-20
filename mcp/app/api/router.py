from fastapi import APIRouter

from app.api.endpoints import auth, ingredients, molecules, pairings

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(ingredients.router)
api_router.include_router(molecules.router)
api_router.include_router(pairings.router)
