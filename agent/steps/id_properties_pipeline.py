# from typing import List
# from llm.instance import llm
# from llm.OpenAi import Model
# from helpers import read_system_prompt
# from model.pipeline import Sequence
# from model.schemas.Properties import Properties
# from model.pipeline import Step, AbortIf


# def find_properties(full_email_dump: str) -> List[dict]:
#     result = llm.chat(
#         message=f"============ Context ============\n{full_email_dump}",
#         system_message=read_system_prompt("id_properties.md"),
#         model=Model.gpt_4_1,
#         response_format=Properties
#     )
#     properties = result.model_dump().get("properties", [])
#     return properties


# find_properties_step = Step(
#     id="find_properties_step",
#     name="Find All Properties",
#     function=lambda _: {
#         "properties": find_properties(email_dump)
#     },
#     start_message=lambda _: "Beginning property scan. Identifying all properties mentioned in the email and any attachments.",
#     end_message=lambda result: (
#         f"Property scan complete. Found {len(result['properties'])} properties: "
#         f"{', '.join([prop['name'] for prop in result['properties']])}"
#         if result["properties"] else "No properties were found in the email."
#     ),
#     message_queue=message_queue
# )


# id_properties_pipeline = lambda email_dump = Sequence([
#     find_properties_step,
#     AbortIf(
#         cond=lambda ctx: len(ctx["find_properties_step"]
#                              ["properties"]) > 0,
#         message="No properties were found."),
#     find_relevant_properties_step
# ])


