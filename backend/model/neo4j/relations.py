from neomodel import AsyncStructuredRel, FloatProperty, StringProperty


class BaseCompositionRel(AsyncStructuredRel):
    unit = StringProperty()
    source_type = StringProperty()


class FoodNutrientRel(BaseCompositionRel):
    value = FloatProperty(required=True)
    value_type = StringProperty()


class FoodCompoundRel(BaseCompositionRel):
    min_concentration = StringProperty()
    max_concentration = StringProperty()
    preparation_type = StringProperty(default="raw")