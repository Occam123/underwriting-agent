## Insurance Underwriting Data Extraction Prompt

You are tasked with extracting **all information necessary to complete an insurance underwriting assessment relevant to a specified property**, based on the provided text.  
The output must match the **JSON schema** below exactly. Your extraction should include every detail required to populate each field **for the one target property** described. **Ignore any data about other properties.**
============  
**Target property**
`<property description>`
============

### Extraction Instructions

1. **Extract every explicit data point from the text that is relevant to the insurance submission, policy, risk, or coverage assessment.**
   - This includes details about the insured, property, construction, sums insured, limits, deductibles, risk factors, claims/loss history, and any other underwriting-relevant fact.
2. **ONLY** take into account data relevant to the stated property
2. **For each data point, provide:**
   - `value`: The information in its **original, correct type** (e.g., as an integer, float, string, boolean, or list, as defined in the output model).
   - `source`: The **verbatim text snippet** from the source document where this value was found.
     - This should be a complete, self-contained fragment; never paraphrase or merge information.
3. **Do not fill in any field unless there is explicit supporting evidence in the source content. If no relevant or matching source is found for a field, leave the value empty. Never guess, infer, assume, or invent values that are not directly supported by the provided text.**
4. **If a `value` must be derived or calculated from the `content`, ensure that the `value` is fully accurate and correctly reflects the information given in the `content`. The extracted `value` must be the precise answer required for the field, even if it requires interpretation, calculation, or normalization from the source `content`. Never copy an imprecise, incomplete, or textual representation to the `value` field, and never misinterpret or incorrectly calculate the value.**
    **Positive Example:**
    ```python
    gross_revenue_or_annual_turnover=Value[int](
        value=5000000,
        content="Gross revenue for last year was approximately five million dollars."
    )
    ```
    **Negative Example (what NOT to do):**
    ```python
    construction_year_build=Value[int](
        value=2006,  # Incorrect: The value should be 2007
        content="The building was constructed the year after 2006."
    )
    ```
    *Do NOT misinterpret or miscalculate the value—always extract the exact correct value required for the field.*
5. **If multiple relevant snippets exist for the same data point, use the one that most directly and completely answers the field. If data is missing, leave the field empty or null but do not invent or infer.**
6. **Do not paraphrase, summarize, or merge information. Do not add, invent, or assume any information.**
7. **Preserve the distinction between types (int, float, string, bool, list) in your output.**
8. **If a field is a list, provide all matching values found, each with its source.**
9. **Only output the data as structured below. Do not add explanations, comments, or extra metadata.**
10. **Format all datetimes in this format: `%d/%m/%Y`**.
11. **If the source is empty do not fill in a value**
12. **Use the given data schema below to determine what each field means**

### data schema

#### `Value<T>`
- **`value`**: The extracted data (type `<T>`), or `null` if missing.
- **`source`**: The exact, verbatim snippet from the document where this value was found, or `null` if not applicable.

#### `Address`
- **`street`** (`Value<string>`): The name of the street for the property’s address.
- **`number`** (`Value<string>`): The street number or lot identifier.
- **`unit`** (`Value<string>`, optional): Apartment/suite/unit number, if any.
- **`postal_code`** (`Value<string>`): The postcode or ZIP code.
- **`city`** (`Value<string>`): The city, town, or municipality.
- **`province`** (`Value<string>`): The state, province, or region.    
- **`country`** (`Value<string>`): The country name.
- **`property_name`** (`Value<string>`, optional): Named estate or building name (e.g., “Maple Apartments”).

#### `ConstructionMaterials`
- **`wood`** (`Value<bool>`): `true` if the primary structure is wood; `false` otherwise.
- **`steel`** (`Value<bool>`): `true` if steel framing or components are used; `false` otherwise.
- **`brick`** (`Value<bool>`): `true` if brick/masonry construction; `false` otherwise.

#### `LocationRisk`
- **`flood_zone`** (`Value<bool>`): `true` if the site lies in a designated flood zone; `false` otherwise.
- **`earthquake_prone_area`** (`Value<bool>`): `true` if within an earthquake‐prone region; `false` otherwise.
- **`windstorm_area`** (`Value<bool>`): `true` if subject to high‐wind or hurricane risk; `false` otherwise.

#### `FireProtection`
- **`sprinklers`** (`Value<bool>`): `true` if an automatic sprinkler system is installed; `false` otherwise.
- **`alarms`** (`Value<bool>`): `true` if fire/ smoke detectors or alarm system present; `false` otherwise.
- **`fire_department_proximity`** (`Value<string>`): Verbatim description or distance to the nearest fire station (e.g., “500 m”, “On-site hydrant”).
    

#### `MinimalInsuranceSubmissionProperty`
- **`total_declared_value`** (`Value<float>`): The insured sum (in the policy currency) declared for this property.
- **`address`** (`Address`): The full postal address of the property (street, number, city, etc.).
- **`business_description`** (`Value<string>`): A brief, verbatim description of the business activities conducted on-site.
- **`property_description`** (`Value<string>`): A detailed, verbatim description of the property itself (type of building, use, size).
- **`construction_materials`** (`ConstructionMaterials`): Which primary building materials apply.
- **`location_risk`** (`LocationRisk`): Flags for natural or environmental hazards at the site.
- **`fire_protection`** (`FireProtection`): Details about installed fire safety measures.
- **`purpose_built_premises`** (`Value<bool>`): Indicates whether the facility was designed and constructed specifically for its current business use (e.g., a purpose‐built cold‐storage warehouse vs. a converted retail space).
- **`established_and_financially_stable`** (`Value<bool>`): Signifies that the business has a proven track record. e.g: audited financials showing stable revenues, profitability, and adequate liquidity.
- **`proactively_risk_managed_and_tested_BCP`** (`Value<bool>`): Reflects whether the insured maintains a formal Business Continuity Plan—regularly reviewed, updated, and exercised (e.g., annual drills, IT failover tests).
- **`engaged_in_the_legal_and_regulatory_landscape_of_their_markets`** (`Value<bool>`): Indicates the business actively monitors and complies with relevant laws, regulations, industry standards, and holds up‐to‐date licenses or certifications.

------------