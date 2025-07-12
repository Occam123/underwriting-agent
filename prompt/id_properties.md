Extract all properties, buildings, or locations that are explicitly subject to insurance in the provided text.

## Instructions:
1. **Identify every individual property, building, address, or sub-location** mentioned as being insured.  
   - If a site contains multiple buildings, structures, or sub-locations described separately, **extract and list each one individually** (even if some details are only available at the site level).
2. For each property, building, or location, provide:
    - The name, number, or identifier (such as the full address, property name, or building number, **copied exactly as shown in the source text**)
    - A brief, fact-based description, including all details on location, usage, occupancy, building structure, construction, fire/security features, and any asset descriptions (**generate a concise and very descriptive summary from which a property can uniquely be identified. Include information to make it uniquely identifiable**)
    - If certain information (e.g., declared values, construction) is only provided at the site level but applies to multiple buildings, **indicate clearly that the information is "site-wide" and attach it to each building or sub-location as applicable**.
3. **List each property, building, or sub-location separately and in full detail.**
4. **DO NOT paraphrase, summarize, or infer any information.** Only copy and organize what is explicitly stated in the source text.
5. **DO NOT delete, omit, or modify any relevant information** about a property, building, or location—even if it seems repetitive.
6. **Structure and format the output so that each property, building, or sub-location appears one after the other, with all original source details presented for each.**

## Critical Rules – MUST FOLLOW:
- **ALWAYS** copy names, addresses, building numbers, and all descriptions directly from the source text—no paraphrasing, no assumptions.
- **ALWAYS** split and organize the output at the most granular level possible: if the text describes multiple buildings or sub-locations, treat each as a separate entity.
- **NEVER** invent or infer information that is not explicitly in the source text.
- **NEVER** delete, omit, or merge any relevant details between properties, buildings, or sub-locations.
- **ALWAYS** format and structure the output as shown below.

## Required Output Format

Property/Location/Building 1:
Name/Address: [copy exactly from source]
Name insured: [copy exactly from source if present]
Description: [copy all relevant details—building, usage, construction, assets, etc.—exactly from source]

Property/Location/Building 2:
Name/Address: [copy exactly from source]
Name insured: [copy exactly from source if present]
Description: [copy all relevant details—building, usage, construction, assets, etc.—exactly from source]

(Continue for every property, building, or sub-location mentioned.)

## Context:
[Paste your source text here]
