from neomodel import StringProperty, FloatProperty, IntegerProperty
from module.knowledge_graph.model.neo4j.base import BaseCompositionRel


class FoodNutrientRel(BaseCompositionRel):
    value = FloatProperty(required=True)
    value_type = StringProperty(default="raw")
    unit = StringProperty(default="mg")


class FoodCompoundRel(BaseCompositionRel):
    foodb_id = IntegerProperty()
    min_concentration = FloatProperty()
    max_concentration = FloatProperty()
    unit = StringProperty(default="mg")
    preparation_type = StringProperty(default="raw")


class EnzymeCompoundRel(BaseCompositionRel):
    foodb_id = IntegerProperty()
    unit = StringProperty(default="unitless")
    preparation_type = StringProperty(default="raw")


class FlavorCompoundRel(BaseCompositionRel):
    foodb_id = IntegerProperty()
    source_node_id = IntegerProperty()
    source_node_type = StringProperty(default="Compound")
