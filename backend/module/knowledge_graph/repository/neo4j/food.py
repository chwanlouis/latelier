from typing import List, Optional
from module.knowledge_graph.model.neo4j.food import Food
from module.knowledge_graph.repository.neo4j.base import NeoModelRepositoryBase
from module.core.tools.log import logger


class FoodRepository(NeoModelRepositoryBase[Food]):
    def __init__(self):
        super().__init__(model_cls=Food)

    async def get_foods_by_group(self, food_group: str) -> List[Food]:
        try:
            return await self.model_cls.nodes.filter(food_group=food_group)
        except Exception as e:
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

    @NeoModelRepositoryBase.read_only_transactional
    async def get_all_food_node(self) -> List[Food]:
        try:
            return await self.model_cls.nodes.order_by("name")
        except Exception as e:
            logger.exception(e)
            raise e


food_repository = FoodRepository()
