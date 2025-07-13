from typing import Literal
from pydantic import BaseModel

MainCategory = Literal[
    "real_estate_and_business_services",
    "manufacturing",
    "retailers",
    "wholesalers",
    "hospitality_sports_and_leisure",
]

SubCategory = Literal[
    # real_estate_and_business_services
    "commercial_real_estate_financial_investors_and_large_building_developers",
    "clerical_technical_and_business_services",
    "local_council_and_state_government_assets",
    "health_centres_hospitals_and_dental_services",
    "community_and_aged_care_facilities",
    # manufacturing
    "wine_drink_and_beverage_manufacturing",
    "metal_fabrication_and_product_manufacturing",
    "electrical_equipment_manufacturing",
    "machinery_manufacturing",
    "food_manufacturing_excluding_eps_direct_heat",
    "brick_stone_concrete_and_plaster_manufacturing",
    # retailers
    "shopping_centres_and_precincts",
    "grocery_store_and_liquor_retailers",
    "household_goods_retailers",
    "pharmaceutical_and_personal_healthcare_retailers",
    "home_improvement_and_hardware_stores",
    "clothing_and_footwear_retailers",
    "printing",
    # wholesalers
    "household_and_electrical_wholesalers",
    "clothing_and_footwear_vendors",
    "machinery_wholesalers",
    # hospitality_sports_and_leisure
    "modern_urban_accommodation_and_hotels",
    "restaurants_cafes_and_hospitality",
    "gyms_and_leisure_centres",
    "modern_sports_stadia",
]

class IndustryType(BaseModel):
    main_category: MainCategory
    sub_category: SubCategory
