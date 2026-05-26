from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    DateTimeProperty,
    ArrayProperty,
    AsyncRelationshipTo
)
from model.neo4j.relations import FoodNutrientRel, FoodCompoundRel


class Food(AsyncStructuredNode):
    food_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    name_scientific = StringProperty(index=True)
    aliases = ArrayProperty(StringProperty(), default=[])
    description = StringProperty()
    food_group = StringProperty(index=True)
    food_subgroup = StringProperty()

    compounds = AsyncRelationshipTo(
        ('model.neo4j.compound.Compound'),
        'CONTAINS_COMPOUND',
        model=FoodCompoundRel
    )

    nutrients = AsyncRelationshipTo(
        ('model.neo4j.nutrient.Nutrient'),
        'HAS_NUTRIENT',
        model=FoodNutrientRel
    )

    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()