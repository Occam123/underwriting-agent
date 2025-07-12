You are given the raw text of an email and a list of properties. Your task is to determine which properties are explicitly referenced, requested, or described in the email.

## Instructions
- **Return only a list** containing the exact `name` values (case, punctuation, spacing) from the provided properties that are relevant to the email content.
- **Do not invent, infer, or paraphrase.** Only select names present in the property list that have clear textual support in the email.
- **Copy property names verbatim.** No summarizing, rephrasing, or partial matches.
- **Do not include commentary, explanations, or formatting.**
- **Your output must be only a list of names, in a valid Python list.**
    
## response_format
`[<property name>, <property name> ...]`