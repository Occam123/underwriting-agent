## Insurance Quotation and Inception Date Extraction Prompt

You are tasked with extracting the **quotation date** and **inception date** from the provided insurance context or document.

- **Quotation date** is any date that indicates when the insurance quote was requested, generated, prepared, issued, or sent.  
    This can appear as "Quote Date", "Quotation Date", "Date of Quote", "Date Quoted", "Quotation Required By", the date on the cover letter or slip, a document creation/modification date, or even the sent date of an email where the quote or request was issued.  
    If several dates seem to fit, prefer the one most clearly labeled, or otherwise the one that is most closely associated with the quote document or correspondence.
    
- **Inception date** is any date that indicates when insurance coverage is scheduled to begin or the policy period starts.  
    This can appear as "Inception Date", "Period of Insurance: From", "Policy Start Date", "With effect from", "Effective Date", "Policy Inception", or similar.  
    Sometimes it is in a range (e.g., "From [date] to [date]"), or referenced as the date coverage commences, or as a scheduled effective date in a table, attachment, or policy schedule.
    

Your extraction should be **strictly evidence-based**: always provide the verbatim source text for each value, and only extract a value if there is clear, direct evidence in the context.

---

### Extraction Instructions

1. **For both "quotation date" and "inception date":**
    
    - **First, find and list all possible candidates** for the date in the provided text or context, using the definitions above as a guide.
        
    - **Reason about which candidate makes the most sense,** based on labels, proximity to relevant sections, typical document structure, or established conventions.
        
    - **Pick the best candidate** and extract only that one.
        
2. **For each date, provide:**
    
    - `date.value`: The date in the original, correct format, strictly as `%d/%m/%Y`.
        
    - `date.source`: The complete, verbatim source text from which the value was obtained. Do not paraphrase or merge information; copy the exact relevant text fragment.
        
    - `reasoning_steps`: A numbered list of your reasoning steps, for example:
        
        1. I located all date-like strings in the context.
            
        2. I identified which strings correspond to a quote request versus policy start.
            
        3. I selected the string most clearly labeled as the quote date (or inception date).
            
3. **Only extract a value if there is explicit, direct evidence in the text.** Never guess, infer, assume, or invent values. If no relevant source text is present, leave `date.value` and `date.source` empty, but still include `reasoning_steps`.
    
4. **If multiple candidates exist, select the one most explicitly labelled** as the "quotation date" or "inception date" by context. If not directly labelled, use the best available supporting evidence (e.g., the date of the quote request, supporting document, or coverage start).
    
5. **Do not paraphrase, summarize, merge, or reinterpret text.** Only use verbatim, complete text fragments as source.
    
6. **Output only the two fields in the schema below.** Do not output anything else, and do not add commentary.
    

---

### Output Schema

quotation_date = {
    "date": {
        "value": "",     # string, format '%d/%m/%Y'
        "source": ""     # verbatim text snippet showing the value in context
    },
    "reasoning_steps": [
        # list of strings describing each reasoning step
    ]
}

inception_date = {
    "date": {
        "value": "",     # string, format '%d/%m/%Y'
        "source": ""     # verbatim text snippet showing the value in context
    },
    "reasoning_steps": [
        # list of strings describing each reasoning step
    ]
}