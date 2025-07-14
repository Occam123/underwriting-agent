from typing import List
from model.pipeline import Step
from model.messageQueue.instance import message_queue

from service.PropertyService import property_service
from service.CaseService import case_service
from agent.AgentContext import agent_ctx


async def create_new_submission(step_ctx) -> None:
    global agent_ctx

    customer_id = step_ctx["get_customer_context_step"]["customer_id"]
    customer_name = step_ctx["find_customer_step"]["customer_name"]
    properties = step_ctx["find_relevant_properties_step"]["properties"]

    existing_properties = []
    for submission in agent_ctx[customer_name]["submissions"]:
        submission_properties = submission["properties"]
        existing_properties.extend(submission_properties.keys())

    property_names = [property["name"] for property in properties]
    new_properties = [
        property_name for property_name in property_names if property_name not in existing_properties]

    if new_properties:
        cases = await case_service.get_cases_by_customer_name(customer_name)
        case_title = f"{customer_name}-{len(cases)+1}"
        case_id = await case_service.create_case(title=case_title, customer_id=customer_id)


        # create new submission for properties
        new_submission = {
            "email_chain": [],
            "submission_info": {},
            "properties": {
                property_name: {
                    "case_id": case_id
                } for property_name in new_properties
            }
        }
        agent_ctx[customer_name]["submissions"].append(new_submission)


    return {
        "new_properties": new_properties,
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
        function=create_new_submission,
        end_message=end_message,
        message_queue=message_queue
    )
