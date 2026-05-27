import enum


class RelationTypeName(str, enum.Enum):
    CONTAINS_COMPOUND = "CONTAINS_COMPOUND"
    HAS_NUTRIENT = "HAS_NUTRIENT"
    HAS_FLAVOR = "HAS_FLAVOR"
    INTERACTS_WITH_ENZYME = "INTERACTS_WITH_ENZYME"


class NodeTypeName(str, enum.Enum):
    Food = "Food"
    Compound = "Compound"
    Nutrient = "Nutrient"
    Flavor = "Flavor"
    Enzyme = "Enzyme"
