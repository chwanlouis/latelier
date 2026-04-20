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
