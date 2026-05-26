# backend/model/neo4j/relations.py
from neomodel import AsyncStructuredRel, StringProperty, FloatProperty, IntegerProperty, DateTimeProperty

class BaseCompositionRel(AsyncStructuredRel):
    """
    Abstract base relationship containing ONLY structural lifecycle 
    auditing fields for global graph consistency.
    """
    source_type = StringProperty(default="UNKNOWN")
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()


class FoodNutrientRel(BaseCompositionRel):
    """Edge: (:Food)-[:HAS_NUTRIENT]->(:Nutrient)"""
    value = FloatProperty(required=True)
    value_type = StringProperty(default="raw")
    unit = StringProperty(default="mg")


class FoodCompoundRel(BaseCompositionRel):
    """Edge: (:Food)-[:CONTAINS_COMPOUND]->(:Compound)"""
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
    """
    Edge: (:Compound)-[:HAS_FLAVOR]->(:Flavor)
    Cleanly tracks unique payload pointers while inheriting
    auditing fields natively from BaseCompositionRel.
    """
    foodb_id = IntegerProperty()
    source_node_id = IntegerProperty()
    source_node_type = StringProperty(default="Compound")