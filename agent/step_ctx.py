step_ctx = {
    "find_customer_step": {
        "customer_name": "[ORGANIZATION_1]"
    },
    "get_customer_context_step": {
        "new": True,
        "customer_name": "[ORGANIZATION_1]",
        "customer_ctx": {
            "submissions": [
                {
                    "email_chain": [],
                    "submission_info": {},
                    "properties": {
                        "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]": {}
                    }
                }
            ]
        }
    },
    "find_properties_step": {
        "properties": [
            {
                "location_id": 1,
                "name": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                "name_insured": "[ORGANIZATION_1] and/or subsidiary companies, more than half the nominal value of whose equity share capital is owned by the named Insured either directly or through other subsidiaries; and any entity over which an Insured exercises management control and any joint venture partner or company for whom an Insured has responsibility for arranging insurance.",
                "description": "Aged care facility. Occupancy: aged care facility. The Business: Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto. Insured assets: All real and personal property (including money) of every kind and description (except as specifically excluded) belonging to the Insured, or for which the Insured is responsible or has assumed responsibility to insure prior to the occurrence of any loss or destruction or damage, including all such property in which the Insured acquires an insurable interest during the Period of Insurance. Declared Values (site-wide): Section 1 - All Property Insured 31,500,000; Section 2 \u2013 Loss of Rent 2,220,000; Combined Declared Value 33,220,000. Limit of Liability: Combined Single Limit Section 1 and 2 48,100,000. Site-wide cover includes Section 1 - Material Loss or Damage, Section 2 - Consequential Loss. Site-wide sub-limits and policy wordings apply as listed in the policy schedule. No further breakdown or identification of individual buildings or sub-locations has been provided in the source text."
            },
            {
                "location_id": 2,
                "name": "anywhere in Australia (including contract sites) where the Insured has property or carries on business, has goods or other property stored or being processed or has work done",
                "name_insured": "[ORGANIZATION_1] and/or subsidiary companies, more than half the nominal value of whose equity share capital is owned by the named Insured either directly or through other subsidiaries; and any entity over which an Insured exercises management control and any joint venture partner or company for whom an Insured has responsibility for arranging insurance.",
                "description": "Site-wide and contract site cover provided across Australia where the Insured has property or carries on business, has goods or other property stored or being processed or has work done (including but not limited to the primary situation at [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]). Insured assets: All real and personal property (including money) of every kind and description (except as specifically excluded) belonging to the Insured, or for which the Insured is responsible or has assumed responsibility to insure prior to the occurrence of any loss or destruction or damage, including all such property in which the Insured acquires an insurable interest during the Period of Insurance. Policy coverage and sub-limits (including those described as site-wide in the schedule) apply at any such location."
            }
        ]
    },
    "find_relevant_properties_step": {
        "properties": [
            {
                "location_id": 1,
                "name": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                "name_insured": "[ORGANIZATION_1] and/or subsidiary companies, more than half the nominal value of whose equity share capital is owned by the named Insured either directly or through other subsidiaries; and any entity over which an Insured exercises management control and any joint venture partner or company for whom an Insured has responsibility for arranging insurance.",
                "description": "Aged care facility. Occupancy: aged care facility. The Business: Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto. Insured assets: All real and personal property (including money) of every kind and description (except as specifically excluded) belonging to the Insured, or for which the Insured is responsible or has assumed responsibility to insure prior to the occurrence of any loss or destruction or damage, including all such property in which the Insured acquires an insurable interest during the Period of Insurance. Declared Values (site-wide): Section 1 - All Property Insured 31,500,000; Section 2 \u2013 Loss of Rent 2,220,000; Combined Declared Value 33,220,000. Limit of Liability: Combined Single Limit Section 1 and 2 48,100,000. Site-wide cover includes Section 1 - Material Loss or Damage, Section 2 - Consequential Loss. Site-wide sub-limits and policy wordings apply as listed in the policy schedule. No further breakdown or identification of individual buildings or sub-locations has been provided in the source text."
            }
        ],
        "summary": None
    },
    "create_new_properties_in_case_step": {
        "new_properties": [
            "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
        ]
    },
    "find_submission_wide_information_step": {
        "submission_info": {
            "quotation_date": {
                "value": "13/07/2025",
                "source": "Verzonden: zondag 13 juli 2025 13:37\nAan: agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org <agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org>\nOnderwerp: [EXTERNAL] New Submission: [ORGANIZATION_1]\n\nHi [NAME_GIVEN_3],\n\nPlease see attached new quote slip for [ORGANIZATION_1]."
            },
            "inception_date": {
                "value": "31/12/2024",
                "source": "PERIOD OF INSURANCE:\nFrom:\n4.00pm 31 December 2024\nTo:\n4.00pm 31 December 2025\nBoth local standard time at the Insured\u2019s head office."
            }
        }
    },
    "extract_structured_data_per_property_step": {
        "structured_data_per_property": {
            "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]": {
                "total_declared_value": {
                    "value": 33220000.0,
                    "source": "Combined Declared Value 33,220,000"
                },
                "address": {
                    "street": {
                        "value": "[LOCATION_ADDRESS_STREET_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "number": {
                        "value": "",
                        "source": ""
                    },
                    "postal_code": {
                        "value": "[LOCATION_ZIP_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "city": {
                        "value": "Epping",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "province": {
                        "value": "VIC",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "country": {
                        "value": "Australia",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\nand anywhere in Australia (including contract sites) where the Insured has property or carries on business"
                    },
                    "unit": {
                        "value": None,
                        "source": ""
                    },
                    "property_name": {
                        "value": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                        "source": "Property name: \"[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\""
                    }
                },
                "business_description": {
                    "value": "Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto.",
                    "source": "THE BUSINESS: Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto."
                },
                "property_description": {
                    "value": "Aged care facility. Occupancy: aged care facility.",
                    "source": "Property description: \"Aged care facility. Occupancy: aged care facility.\""
                },
                "construction_materials": {
                    "wood": {
                        "value": None,
                        "source": ""
                    },
                    "steel": {
                        "value": None,
                        "source": ""
                    },
                    "brick": {
                        "value": None,
                        "source": ""
                    }
                },
                "location_risk": {
                    "flood_zone": {
                        "value": None,
                        "source": ""
                    },
                    "earthquake_prone_area": {
                        "value": None,
                        "source": ""
                    },
                    "windstorm_area": {
                        "value": None,
                        "source": ""
                    }
                },
                "fire_protection": {
                    "sprinklers": {
                        "value": None,
                        "source": ""
                    },
                    "alarms": {
                        "value": None,
                        "source": ""
                    },
                    "fire_department_proximity": {
                        "value": None,
                        "source": ""
                    }
                },
                "purpose_built_premises": {
                    "value": None,
                    "source": ""
                },
                "established_and_financially_stable": {
                    "value": None,
                    "source": ""
                },
                "proactively_risk_managed_and_tested_BCP": {
                    "value": None,
                    "source": ""
                },
                "engaged_in_the_legal_and_regulatory_landscape_of_their_markets": {
                    "value": None,
                    "source": ""
                },
                "industry_type": {
                    "main_category": "real_estate_and_business_services",
                    "sub_category": "community_and_aged_care_facilities"
                }
            }
        }
    },
    "aggregate_data_step": {
        "submission_info": {
            "quotation_date": {
                "value": "13/07/2025",
                "source": "Verzonden: zondag 13 juli 2025 13:37\nAan: agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org <agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org>\nOnderwerp: [EXTERNAL] New Submission: [ORGANIZATION_1]\n\nHi [NAME_GIVEN_3],\n\nPlease see attached new quote slip for [ORGANIZATION_1]."
            },
            "inception_date": {
                "value": "31/12/2024",
                "source": "PERIOD OF INSURANCE:\nFrom:\n4.00pm 31 December 2024\nTo:\n4.00pm 31 December 2025\nBoth local standard time at the Insured\u2019s head office."
            }
        },
        "structured_data_per_property": {
            "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]": {
                "total_declared_value": {
                    "value": 33220000.0,
                    "source": "Combined Declared Value 33,220,000"
                },
                "address": {
                    "street": {
                        "value": "[LOCATION_ADDRESS_STREET_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "number": {
                        "value": "",
                        "source": ""
                    },
                    "postal_code": {
                        "value": "[LOCATION_ZIP_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "city": {
                        "value": "Epping",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "province": {
                        "value": "VIC",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "country": {
                        "value": "Australia",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\nand anywhere in Australia (including contract sites) where the Insured has property or carries on business"
                    },
                    "unit": {
                        "value": None,
                        "source": ""
                    },
                    "property_name": {
                        "value": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                        "source": "Property name: \"[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\""
                    }
                },
                "business_description": {
                    "value": "Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto.",
                    "source": "THE BUSINESS: Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto."
                },
                "property_description": {
                    "value": "Aged care facility. Occupancy: aged care facility.",
                    "source": "Property description: \"Aged care facility. Occupancy: aged care facility.\""
                },
                "construction_materials": {
                    "wood": {
                        "value": None,
                        "source": ""
                    },
                    "steel": {
                        "value": None,
                        "source": ""
                    },
                    "brick": {
                        "value": None,
                        "source": ""
                    }
                },
                "location_risk": {
                    "flood_zone": {
                        "value": None,
                        "source": ""
                    },
                    "earthquake_prone_area": {
                        "value": None,
                        "source": ""
                    },
                    "windstorm_area": {
                        "value": None,
                        "source": ""
                    }
                },
                "fire_protection": {
                    "sprinklers": {
                        "value": None,
                        "source": ""
                    },
                    "alarms": {
                        "value": None,
                        "source": ""
                    },
                    "fire_department_proximity": {
                        "value": None,
                        "source": ""
                    }
                },
                "purpose_built_premises": {
                    "value": None,
                    "source": ""
                },
                "established_and_financially_stable": {
                    "value": None,
                    "source": ""
                },
                "proactively_risk_managed_and_tested_BCP": {
                    "value": None,
                    "source": ""
                },
                "engaged_in_the_legal_and_regulatory_landscape_of_their_markets": {
                    "value": None,
                    "source": ""
                },
                "industry_type": {
                    "main_category": "real_estate_and_business_services",
                    "sub_category": "community_and_aged_care_facilities"
                }
            }
        }
    },
    "clean_data_step": {
        "submission_info": {
            "quotation_date": {
                "value": "13/07/2025",
                "source": "Verzonden: zondag 13 juli 2025 13:37\nAan: agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org <agent@sandboxff7d39e85317487d80365a97016fa68a.mailgun.org>\nOnderwerp: [EXTERNAL] New Submission: [ORGANIZATION_1]\n\nHi [NAME_GIVEN_3],\n\nPlease see attached new quote slip for [ORGANIZATION_1]."
            },
            "inception_date": {
                "value": "31/12/2024",
                "source": "PERIOD OF INSURANCE:\nFrom:\n4.00pm 31 December 2024\nTo:\n4.00pm 31 December 2025\nBoth local standard time at the Insured\u2019s head office."
            }
        },
        "structured_data_per_property": {
            "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]": {
                "total_declared_value": {
                    "value": 33220000.0,
                    "source": "Combined Declared Value 33,220,000"
                },
                "address": {
                    "street": {
                        "value": "[LOCATION_ADDRESS_STREET_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "number": {
                        "value": None,
                        "source": None
                    },
                    "postal_code": {
                        "value": "[LOCATION_ZIP_2]",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "city": {
                        "value": "Epping",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "province": {
                        "value": "VIC",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]"
                    },
                    "country": {
                        "value": "Australia",
                        "source": "SITUATION AND/OR PREMISES: [LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\nand anywhere in Australia (including contract sites) where the Insured has property or carries on business"
                    },
                    "unit": {
                        "value": None,
                        "source": None
                    },
                    "property_name": {
                        "value": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                        "source": "Property name: \"[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]\""
                    }
                },
                "business_description": {
                    "value": "Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto.",
                    "source": "THE BUSINESS: Principally, property owners of aged care facilities including retirement facilities, including all associated activities past or present, and any other incidental occupations or activities incidental thereto."
                },
                "property_description": {
                    "value": "Aged care facility. Occupancy: aged care facility.",
                    "source": "Property description: \"Aged care facility. Occupancy: aged care facility.\""
                },
                "construction_materials": {
                    "wood": {
                        "value": False,
                        "source": "Updated in process config"
                    },
                    "steel": {
                        "value": None,
                        "source": None
                    },
                    "brick": {
                        "value": None,
                        "source": None
                    }
                },
                "location_risk": {
                    "flood_zone": {
                        "value": None,
                        "source": None
                    },
                    "earthquake_prone_area": {
                        "value": None,
                        "source": None
                    },
                    "windstorm_area": {
                        "value": None,
                        "source": None
                    }
                },
                "fire_protection": {
                    "sprinklers": {
                        "value": None,
                        "source": None
                    },
                    "alarms": {
                        "value": None,
                        "source": None
                    },
                    "fire_department_proximity": {
                        "value": None,
                        "source": None
                    }
                },
                "purpose_built_premises": {
                    "value": None,
                    "source": None
                },
                "established_and_financially_stable": {
                    "value": None,
                    "source": None
                },
                "proactively_risk_managed_and_tested_BCP": {
                    "value": None,
                    "source": None
                },
                "engaged_in_the_legal_and_regulatory_landscape_of_their_markets": {
                    "value": None,
                    "source": None
                },
                "industry_type": {
                    "main_category": "real_estate_and_business_services",
                    "sub_category": "community_and_aged_care_facilities"
                }
            }
        }
    },
    "apply_appetite_matrix_step": {
        "appetite_evaluation": {
            "in_appetite_properties": [],
            "out_of_appetite_properties": [
                {
                    "name": "[LOCATION_ADDRESS_STREET_2], Epping VIC [LOCATION_ZIP_2]",
                    "reason": [
                        0,
                        1,
                        4
                    ]
                }
            ]
        }
    },
    "check_quick_decline_rules_data": {
        "missing_values": []
    },
    "apply_quick_decline_rules_step": {
        "decline_reasons": [
            "Decline: The policy inception date is before the quote date."
        ]
    }
}
