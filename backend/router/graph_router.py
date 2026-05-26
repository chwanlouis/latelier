from fastapi import APIRouter, Depends, HTTPException, Query, status
from router.auth_router import get_current_user
from repository.neo4j.graph import graph_repository
from model.response.graph import GraphResponse
from tools.log import logger

graph_router = APIRouter(prefix="/graph", tags=["Graph"])


@graph_router.get(
    path="/food/{food_id}",
    response_model=GraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve subgraph centred on a single food node",
    description=(
        "Returns all nodes and edges reachable within one hop from the specified "
        "food, including its compounds, nutrients, and the flavors of those compounds."
    ),
)
async def get_food_subgraph(
    food_id: str,
    current_user=Depends(get_current_user),
):
    try:
        return await graph_repository.get_food_subgraph(food_id=food_id)
    except Exception as exc:
        logger.error(f"GET /graph/food/{food_id} failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve food subgraph from Neo4j",
        )


@graph_router.get(
    path="/foods",
    response_model=GraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a paged food graph",
    description=(
        "Returns a paginated graph of food nodes together with their directly "
        "connected compounds and nutrients."
    ),
)
async def get_foods_graph(
    skip: int = Query(default=0, ge=0, description="Number of food nodes to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of food nodes to return"),
    current_user=Depends(get_current_user),
):
    try:
        return await graph_repository.get_foods_graph(skip=skip, limit=limit)
    except Exception as exc:
        logger.error(f"GET /graph/foods failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve foods graph from Neo4j",
        )
