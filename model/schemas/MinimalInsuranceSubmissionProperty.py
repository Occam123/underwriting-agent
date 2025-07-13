from pydantic import BaseModel
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

class Value(BaseModel, Generic[T]):
    value: Optional[T]
    source: Optional[str] = None

class Address(BaseModel):
    street: Value[str]
    number: Value[str]
    postal_code: Value[str]
    city: Value[str]
    province: Value[str]
    country: Value[str]
    unit: Optional[Value[str]] = None
    property_name: Optional[Value[str]] = None

class ConstructionMaterials(BaseModel):
    wood: Value[bool]
    steel: Value[bool]
    brick: Value[bool]

class LocationRisk(BaseModel):
    flood_zone: Value[bool]
    earthquake_prone_area: Value[bool]
    windstorm_area: Value[bool]

class FireProtection(BaseModel):
    sprinklers: Value[bool]
    alarms: Value[bool]
    fire_department_proximity: Value[str]

class MinimalInsuranceSubmissionProperty(BaseModel):
    total_declared_value: Value[float]
    address: Address
    business_description: Value[str]
    property_description: Value[str]
    construction_materials: ConstructionMaterials
    location_risk: LocationRisk
    fire_protection: FireProtection
    purpose_built_premises: Value[bool]
    established_and_financially_stable: Value[bool]
    proactively_risk_managed_and_tested_BCP: Value[bool]
    engaged_in_the_legal_and_regulatory_landscape_of_their_markets: Value[bool]
