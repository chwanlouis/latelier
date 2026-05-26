from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    IntegerProperty,
    BooleanProperty,
    DateTimeProperty,
    AsyncRelationshipFrom
)
from model.neo4j.relations import FoodNutrientRel


class Nutrient(AsyncStructuredNode):
    foodb_id = IntegerProperty(unique_index=True, required=True)
    nutrient_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    legacy_id = IntegerProperty()
    export = BooleanProperty(default=False)
    state = StringProperty()
    annotation_quality = StringProperty()
    description = StringProperty()
    wikipedia_id = StringProperty()
    comments = StringProperty()
    dfc_id = StringProperty()
    duke_id = StringProperty()
    eafus_id = StringProperty()
    dfc_name = StringProperty()
    compound_source = StringProperty()
    metabolism = StringProperty()
    synthesis_citations = StringProperty()
    general_citations = StringProperty()
    creator_id = IntegerProperty()
    updater_id = IntegerProperty()
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()

    foods = AsyncRelationshipFrom(
        ('model.neo4j.food.Food'),
        'HAS_NUTRIENT',
        model=FoodNutrientRel
    )
