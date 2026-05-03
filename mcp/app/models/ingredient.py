from pydantic import BaseModel
from typing import Optional


class Molecule(BaseModel):
    id: str
    name: str
    smiles: str
    cas_number: Optional[str] = None
    flavor_profile: Optional[list[str]] = None


class Ingredient(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    molecules: Optional[list[Molecule]] = None


class PairingScore(BaseModel):
    ingredient_a: str
    ingredient_b: str
    score: float
    shared_molecules: list[str]
    soap_risk: bool = False


class GeneticFilterResult(BaseModel):
    ingredient: str
    has_or6a2_risk: bool
    aldehyde_molecules: list[str]


class Technique(BaseModel):
    name: str
    type: str  # Thermal, Chemical, or Mechanical


class Recipe(BaseModel):
    id: str
    title: str
    instructions: str
    techniques: Optional[list[Technique]] = None


class DishPreference(BaseModel):
    """A user preference for a specific technique+ingredient combination."""
    technique: str   # e.g., "Grilling", "Steaming"
    ingredient: str  # e.g., "steak", "fish"


class PreferenceRecommendation(BaseModel):
    preference: DishPreference
    recipes: list[Recipe]
