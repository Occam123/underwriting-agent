from typing import List
from model.Email import Email
from model.pipeline import Step
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.Basic import ListOfStrings
from model.messageQueue.instance import message_queue
from helpers import json_dump

AgentContext = dict


def find_relevant_properties(email_dump_without_attachments: str, properties: List[dict]) -> List[dict]:
    context = f"============== Email ==============\n{email_dump_without_attachments}\n\n============== Properties ==============\n{json_dump(properties)}"
    result = llm.chat(
        message=f"Context:\n{context}",
        system_message=read_system_prompt("relevant_properties.md"),
        model=Model.o4_mini,
        response_format=ListOfStrings,
        reasoning={
            "effort": "high",
            "summary": "detailed"
        }
    )
    relevant_property_names = result["result"].model_dump(
    )["values"] if result["result"] else None

    relevant_properties = [
        property for property in properties
        if property["name"] in relevant_property_names
    ]
    return {
        "result": relevant_properties,
        "summary": result.get("summary")
    }


def find_relevant_properties_step(email: Email):
    def start_message(_):
        return (
            "I am determining which properties are relevant to this inquiry."
        )

    def end_message(step_result, _):
        props = step_result["properties"]
        if not props:
            return "I did not find any properties relevant to this email."
        if len(props) == 1:
            return f"The relevant property is: {props[0]['name']}."
        prop_list = "; ".join([prop['name'] for prop in props])
        return f"The relevant properties are: {prop_list}."

    def result(step_ctx: dict):
        relevant_properties = find_relevant_properties(
            email_dump_without_attachments=email.dump(dump_attachments=False),
            properties=step_ctx["find_properties_step"]["properties"]
        )
        return {
            "properties": relevant_properties["result"],
            "summary": relevant_properties["summary"]
        }

    return Step(
        id="find_relevant_properties_step",
        name="Find Relevant Properties to Email",
        function=lambda step_ctx: result(step_ctx),
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )