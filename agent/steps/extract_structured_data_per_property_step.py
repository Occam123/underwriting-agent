from typing import List
from model.Email import Email
from model.pipeline import Step
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.Properties import Properties
from model.messageQueue.instance import message_queue
from model.schemas.MinimalInsuranceSubmissionProperty import MinimalInsuranceSubmissionProperty
from model.schemas.IndustryType import IndustryType
from service.PropertyService import property_service
from helpers import json_dump
from agent.AgentContext import agent_ctx


def determine_industry_type(context: str) -> dict:
    result = llm.chat(
        message=f"================== Context ==================\n{context}",
        system_message=read_system_prompt("determine_industry_type.md"),
        response_format=IndustryType,
        model=Model.o4_mini,
        reasoning={
            "effort": "medium",
            "summary": "detailed"
        }
    )
    return {
        "result": result["result"].model_dump() if result["result"] else None,
        "summary": result.get("summary")
    }


def extract_structured_data(context: str) -> dict:
    result = llm.chat(
        message=context,
        system_message=read_system_prompt("extract_structured_data.md"),
        model=Model.gpt_4_1,
        response_format=MinimalInsuranceSubmissionProperty
    )
    return result.model_dump()


def find_case_id(customer_name: str, property_name: str) -> str:
    """
    Search all submissions for this customer, find the one that
    contains `property_name`, and return its case_id.id
    """
    subs = agent_ctx[customer_name].get("submissions", [])
    for submission in subs:
        props = submission.get("properties", {})
        if property_name in props:
            case_obj = props[property_name].get("case_id")
            # if case_obj is already a string, just return it
            if isinstance(case_obj, str):
                return case_obj
            # otherwise assume dict with "id" key
            return case_obj.id
    raise KeyError(f"No case found for property '{property_name}'")


async def extract_structured_date_per_property(step_ctx: dict, email_dump: str) -> dict:
    global agent_ctx

        # relevant_properties: List[dict], customer_name: str, email_dump: str) -> dict:
    relevant_properties = step_ctx["find_relevant_properties_step"]["properties"]
    customer_name=step_ctx["find_customer_step"]["customer_name"]
    
    structured_data_per_property = {}

    for property in relevant_properties:
        property_name = property['name']
        property_description = property['description']

        property_context = f'Property name: "{property_name}"\nProperty description: "{property_description}"'
        context = f"============ Target property ============\n{property_context}\n\n============ Context ============\n{email_dump}"

        structured_data = extract_structured_data(context)
        structured_data_per_property[property_name] = structured_data

        property_description = structured_data["property_description"]["value"]
        business_description = structured_data["business_description"]["value"]

        # TODO: improve
        context = f'================== Context ==================\nProperty name: "{property_name}"\nProperty description: "{property_description}"\nBusiness description: {business_description}'
        result = determine_industry_type(context)
        industry_type = result["result"]
        structured_data_per_property[property_name]["industry_type"] = industry_type

        # building_id = property.id
        
        print(json_dump(agent_ctx))
        case_id = find_case_id(customer_name, property_name)

        await property_service.create_building(
            case_id=case_id,
            name=property_name,
            structured_data=structured_data
        )

    return structured_data_per_property


def extract_structured_data_per_property_step(email: Email) -> Step:
    def start_message(_):
        return "I am extracting detailed structured data for each relevant property."

    def end_message(step_result, _):
        data_map = step_result.get("structured_data_per_property", {})
        if not data_map:
            return "I did not extract any structured data for the properties."
        entries = []
        for prop, data in data_map.items():
            serialized = json_dump(data)
            entries.append(f"{prop}:\n{serialized}")
        joined = "\n\n".join(entries)
        return f"I have extracted structured data for each property:\n\n{joined}"
    

    async def worker(step_ctx: dict) -> dict:
        # here we "integrate" the email_dump
        result_map = await extract_structured_date_per_property(
            step_ctx=step_ctx,
            email_dump=email.dump()
        )
        return {"structured_data_per_property": result_map}


    return Step(
        id="extract_structured_data_per_property_step",
        name="Extract Structured Data Per Property",
        function=worker,
        # function=lambda step_ctx: {
        #     "structured_data_per_property": extract_structured_date_per_property(
        #         relevant_properties=step_ctx["find_relevant_properties_step"]["properties"],
        #         customer_name=step_ctx["find_customer_step"]["customer_name"],
        #         email_dump=email.dump()
        #     )
        # },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )
