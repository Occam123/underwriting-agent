from typing import List
from model.Email import Email
from model.pipeline import Step
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.Properties import Properties
from model.messageQueue.instance import message_queue


def find_properties(full_email_dump: str) -> List[dict]:
    result = llm.chat(
        message=f"============ Context ============\n{full_email_dump}",
        system_message=read_system_prompt("id_properties.md"),
        model=Model.gpt_4_1,
        response_format=Properties
    )
    properties = result.model_dump().get("properties", [])
    return properties


def find_properties_step(email: Email) -> Step:
    def start_message(_):
        return (
            "I am reviewing the email and attachments to identify all mentioned properties."
        )

    def end_message(step_result, _):
        props = step_result["properties"]
        if not props:
            return "I did not identify any properties in the provided correspondence."
        if len(props) == 1:
            return f"I identified 1 property: {props[0]['name']}."
        prop_list = "; ".join([prop['name'] for prop in props])
        return f"I identified {len(props)} properties: {prop_list}."

    return Step(
        id="find_properties_step",
        name="Find All Properties",
        function=lambda _: {"properties": find_properties(email.dump())},
        # start_message=start_message,
        # end_message=end_message,
        message_queue=message_queue
    )
