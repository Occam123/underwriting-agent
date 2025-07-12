from typing import List, Optional
from model.Email import Email
from model.pipeline import Sequence
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.pipeline import Sequence
from model.schemas.Properties import Properties
from model.pipeline import Step, AbortIf
from model.messageQueue.MessageQueue import MessageQueue
from model.schemas.Basic import ListOfStrings, StringValue
from model.messageQueue.MessageQueue import Message
from helpers import json_dump
from exceptions import StopExecution
from model.messageQueue.instance import message_queue

from service.CaseService import case_service
from service.LogService import log_service
from service.CustomerService import CustomerService


def find_properties(full_email_dump: str) -> List[dict]:
    result = llm.chat(
        message=f"============ Context ============\n{full_email_dump}",
        system_message=read_system_prompt("id_properties.md"),
        model=Model.gpt_4_1,
        response_format=Properties
    )
    properties = result.model_dump().get("properties", [])
    return properties


def find_properties_step(email: Email, message_queue: MessageQueue) -> Step:
    return Step(
        id="find_properties_step",
        name="Find All Properties",
        function=lambda _: {
            "properties": find_properties(email.dump())
        },
        start_message=lambda _: "Beginning property scan. Identifying all properties mentioned in the email and any attachments.",
        end_message=lambda result: (
            f"Property scan complete. Found {len(result['properties'])} properties: "
            f"{', '.join([prop['name'] for prop in result['properties']])}"
            if result["properties"] else "No properties were found in the email."
        ),
        message_queue=message_queue
    )


def find_relevant_properties(email_dump_without_attachments: str, properties: List[dict]) -> List[dict]:
    context = f"============== Email ==============\n{email_dump_without_attachments}\n\n============== Properties ==============\n{json_dump(properties)}"
    result = llm.chat(
        message=f"Context:\n{context}",
        system_message=read_system_prompt("relevant_properties.md"),
        model=Model.gpt_4_1,
        response_format=ListOfStrings
    )
    relevant_property_names = result.model_dump()["values"]
    relevant_properties = [
        property for property in properties
        if property["name"] in relevant_property_names
    ]
    return relevant_properties


def find_relevant_properties_step(email: Email):
    return Step(
        id="find_relevant_properties_step",
        name="Find Relevant Properties to Email",
        function=lambda ctx: {
            "properties": find_relevant_properties(
                email.dump(dump_attachments=False), ctx["find_properties_step"]["properties"])
        },
        start_message=lambda _: (
            "Identifying which of the discovered properties are relevant to the content of this email and its attachments."
        ),
        end_message=lambda result: (
            f"Relevant properties identified: "
            f"{', '.join([prop['name'] for prop in result['properties']])}"
            if result["properties"] else "No relevant properties were found in the email."
        ),
        message_queue=message_queue
    )


def find_customer(email: Email) -> Optional[str]:
    context = f"============== Email ==============\n{email.dump()}"
    result = llm.chat(
        message=f"Context:\n{context}",
        system_message=read_system_prompt("id_customer.md"),
        model=Model.gpt_4_1,
        response_format=StringValue
    )
    return result.model_dump().get("value", None)


def gen_id_properties_pipeline(email: Email, message_queue: MessageQueue):
    return Sequence([
        find_properties_step(email, message_queue),
        AbortIf(
            cond=lambda ctx: len(ctx["find_properties_step"]
                                 ["properties"]) > 0,
            message="No properties were found."),
        find_relevant_properties_step(email),
        AbortIf(
            cond=lambda ctx: len(ctx["find_properties_step"]
                                 ["properties"]) > 0,
            message="No relevant properties were found.")
    ])



"""
context = {
    "customer1": {
        "cases": {
            "case1": {
                "email_chain": [
                    Email(id="...."),
                    Email(id="...."),
                    Email(id="...."),
                ]
                "submission_info": {...}
                "properties": {
                    "property1": {...},
                    "property2": {...}
                }
            },
            "case2": {
                "email_chain": [],
                "submission_info": {...}
                "properties": {
                    "property1": {...}
                }
            }
        }
    }
}
"""

agent_context = {}


async def run_agent(email: Email) -> None:
    id_properties_pipeline = gen_id_properties_pipeline(email, message_queue)

    ctx = {}
    id_properties_pipeline.execute(ctx)

    try:
        new_ctx = id_properties_pipeline.execute(ctx)

        property = new_ctx["find_relevant_properties_step"]["properties"].keys()[0]
        property_name = property["name"]

        

        case_service.create_case()
        case = await case_service.create_case(title=property_name)
        print(case)

        


        print("\n\n")
    except StopExecution as e:
        message_queue.push(Message(e.message))

