from typing import List, Optional
from model.neo4j.food import Food
from repository.neo4j.base import NeoModelRepositoryBase


class FoodRepository(NeoModelRepositoryBase[Food]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of FoodRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.food_repository import food_repository"
            )
        super().__init__(model_cls=Food)

    async def get_foods_by_group(self, food_group: str) -> List[Food]:
        try:
            return await self.model_cls.nodes.filter(food_group=food_group)
        except Exception as e:
            from tools.log import logger
            logger.error(f"Failed to filter foods by group '{food_group}': {e}")
            raise e

    @NeoModelRepositoryBase.transactional
    async def update_food_description(self, food_id: str, new_description: str) -> Optional[Food]:
        food_node = await self.get_by_property("food_id", food_id)
        if food_node:
            food_node.description = new_description
            await food_node.save()
            return food_node
        return None


_GUARD_TOKEN = object()
food_repository = FoodRepository(_internal_token=_GUARD_TOKEN)