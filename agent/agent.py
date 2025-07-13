from typing import List, Optional
from traceback import print_exc
import json
from model.Email import Email
from model.pipeline import Sequence, Step, AbortIf, InspectNode
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.Properties import Properties
from model.messageQueue.MessageQueue import MessageQueue, Message
from model.schemas.Basic import ListOfStrings, StringValue
from helpers import json_dump
from exceptions import StopExecution
from model.messageQueue.instance import message_queue

from service.CaseService import case_service
from service.LogService import log_service
from service.CustomerService import CustomerService
AgentContext = dict

agent_ctx: AgentContext = {
}


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

    return Step(
        id="find_relevant_properties_step",
        name="Find Relevant Properties to Email",
        function=lambda step_ctx: {
            "properties": find_relevant_properties(
                email.dump(dump_attachments=False), step_ctx["find_properties_step"]["properties"])
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def find_customer_based_on_email_content(email: Email) -> Optional[str]:
    context = f"============== Email ==============\n{email.dump()}"
    result = llm.chat(
        message=f"============== Context ==============\n{context}",
        system_message=read_system_prompt("id_customer.md"),
        model=Model.o4_mini,
        response_format=StringValue,
        reasoning={
            "effort": "medium",
            "summary": "detailed"
        }
    )
    return {
        "result": result["result"].model_dump()["value"] if result["result"] else None,
        "summary": result.get("summary")
    }


def find_customer_based_on_email_chain(email: Email) -> Optional[str]:
    previous_email_id = email.previous_email_id
    for customer_name, submissions in agent_ctx.items():
        for submission in submissions:
            email_chain = submission.get("email_chain", [])
            email_chain_ids = [email.id for email in email_chain]
            if previous_email_id in email_chain_ids:
                return customer_name
    return None


def find_customer(email: Email) -> Optional[str]:
    customer_name = find_customer_based_on_email_chain(email)
    if customer_name is not None:
        return customer_name

    result = find_customer_based_on_email_content(email)
    customer_name = result["result"]
    return customer_name


def find_customer_step(email: Email):
    def start_message(_):
        return "I am analyzing the email to identify the associated customer or organization."

    def end_message(step_result, _):
        name = step_result["customer_name"]
        if name:
            return f"The customer associated with this inquiry is: {name}."
        else:
            return "I could not confidently assign a customer to this inquiry."

    return Step(
        id="find_customer_step",
        name="Find Customer Step",
        function=lambda _: {
            "customer_name": find_customer(email)
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def get_customer_context(customer_name: str):
    customer_ctx = agent_ctx.get(customer_name)
    if customer_ctx is None:
        default_ctx = {
            "submissions": []
        }
        agent_ctx[customer_name] = default_ctx
        return {
            "new": True,
            "customer_name": customer_name,
            "customer_ctx": default_ctx
        }
    return {
        "new": False,
        "customer_name": customer_name,
        "customer_ctx": customer_ctx
    }


def get_customer_context_step():
    def start_message(step_ctx):
        return f"I am checking if {step_ctx['find_customer_step']['customer_name']} has an existing case in the system."

    def end_message(step_result, _):
        if step_result["new"]:
            return (
                f"No existing submission found for {step_result['customer_name']}. I have created a new submission."
            )
        else:
            return (
                f"A case already exists for {step_result['customer_name']}."
            )

    return Step(
        id="get_customer_context_step",
        name="Get Customer Context Step",
        function=lambda step_ctx: get_customer_context(
            step_ctx["find_customer_step"]["customer_name"]),
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def create_new_submission(customer_name: str, properties: List[dict]) -> None:
    existing_properties = []
    for submission in agent_ctx[customer_name]["submissions"]:
        submission_properties = submission["properties"]
        existing_properties.extend(submission_properties.keys())

    property_names = [property["name"] for property in properties]
    new_properties = [
        property_name for property_name in property_names if property_name not in existing_properties]

    if new_properties:
        # create new submission for properties
        new_submission = {
            "email_chain": [],
            "submission_info": {},
            "properties": {
                property_name: {} for property_name in new_properties
            }
        }
        agent_ctx[customer_name]["submissions"].append(new_submission)

    return {
        "new_properties": new_properties
    }


def create_new_submission_step():
    def end_message(step_result, step_ctx):
        customer = step_ctx["find_customer_step"]["customer_name"]
        properties = step_result.get("new_properties", [])
        if not properties:
            return f"No new properties were added for {customer}. All properties already exist in an other submission."
        if len(properties) == 1:
            props_display = properties[0]
        else:
            props_display = "; ".join(properties)
        return (
            f"I have added the following new {'property' if len(properties)==1 else 'properties'} for {customer}: {props_display}."
        )

    return Step(
        id="create_new_properties_in_case_step",
        name="Create Properties in Case Step",
        function=lambda step_ctx: create_new_submission(
            step_ctx["find_customer_step"]["customer_name"],
            step_ctx["find_relevant_properties_step"]["properties"]
        ),
        end_message=end_message,
        message_queue=message_queue
    )


def gen_id_properties_pipeline(email: Email):
    return Sequence([
        find_customer_step(email),
        # InspectNode(),
        AbortIf(
            cond=lambda step_ctx: step_ctx["find_customer_step"]["customer_name"] is None,
            message="I could not identify a customer. Please provide more information about the intended customer and resend your request."
        ),
        get_customer_context_step(),
        find_properties_step(email),
        AbortIf(
            cond=lambda step_ctx: not step_ctx["find_properties_step"]["properties"],
            message="No properties were found in the email or its attachments."
        ),
        find_relevant_properties_step(email),
        AbortIf(
            cond=lambda step_ctx: not step_ctx["find_relevant_properties_step"]["properties"],
            message="No relevant properties could be identified for this email."
        ),
        create_new_submission_step()
    ])


"""
context = {
    "customer1": {
        "submissions": [
            {
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
            {
                "email_chain": [],
                "submission_info": {...}
                "properties": {
                    "property1": {...}
                }
            }
        ]
    }
}
"""


async def run_agent(email: Email) -> None:
    id_properties_pipeline = gen_id_properties_pipeline(email)
    step_ctx = {}
    try:
        result = id_properties_pipeline.execute(step_ctx)
        print(json.dumps(agent_ctx, indent=2))
        print("\n\n")
    except StopExecution as e:
        message_queue.push(Message(e.message))
    except Exception as e:
        print("Error whilst executing pipeline")
        print(e)
        print_exc()
