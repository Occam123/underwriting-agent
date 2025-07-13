from typing import List, Optional, Dict
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
from model.schemas.ISRDates import ISRDates
from model.schemas.IndustryType import IndustryType
from model.schemas.MinimalInsuranceSubmissionProperty import MinimalInsuranceSubmissionProperty
from helpers import json_dump, string_to_datetime
from exceptions import StopExecution
from model.messageQueue.instance import message_queue

from agent.clean_properties import clean_properties

from service.CaseService import case_service
from service.LogService import log_service
from service.CustomerService import CustomerService
from config.Config import config
from datetime import datetime

from agent.steps.find_properties_step import find_properties_step
from agent.steps.find_relevant_properties_step import find_relevant_properties_step


AgentContext = dict

agent_ctx: AgentContext = {
}


# def find_properties(full_email_dump: str) -> List[dict]:
#     result = llm.chat(
#         message=f"============ Context ============\n{full_email_dump}",
#         system_message=read_system_prompt("id_properties.md"),
#         model=Model.gpt_4_1,
#         response_format=Properties
#     )
#     properties = result.model_dump().get("properties", [])
#     return properties


# def find_properties_step(email: Email) -> Step:
#     def start_message(_):
#         return (
#             "I am reviewing the email and attachments to identify all mentioned properties."
#         )

#     def end_message(step_result, _):
#         props = step_result["properties"]
#         if not props:
#             return "I did not identify any properties in the provided correspondence."
#         if len(props) == 1:
#             return f"I identified 1 property: {props[0]['name']}."
#         prop_list = "; ".join([prop['name'] for prop in props])
#         return f"I identified {len(props)} properties: {prop_list}."

#     return Step(
#         id="find_properties_step",
#         name="Find All Properties",
#         function=lambda _: {"properties": find_properties(email.dump())},
#         # start_message=start_message,
#         # end_message=end_message,
#         message_queue=message_queue
#     )


# def find_relevant_properties(email_dump_without_attachments: str, properties: List[dict]) -> List[dict]:
#     context = f"============== Email ==============\n{email_dump_without_attachments}\n\n============== Properties ==============\n{json_dump(properties)}"
#     result = llm.chat(
#         message=f"Context:\n{context}",
#         system_message=read_system_prompt("relevant_properties.md"),
#         model=Model.o4_mini,
#         response_format=ListOfStrings,
#         reasoning={
#             "effort": "high",
#             "summary": "detailed"
#         }
#     )
#     relevant_property_names = result["result"].model_dump(
#     )["values"] if result["result"] else None

#     relevant_properties = [
#         property for property in properties
#         if property["name"] in relevant_property_names
#     ]
#     return {
#         "result": relevant_properties,
#         "summary": result.get("summary")
#     }


# def find_relevant_properties_step(email: Email):
#     def start_message(_):
#         return (
#             "I am determining which properties are relevant to this inquiry."
#         )

#     def end_message(step_result, _):
#         props = step_result["properties"]
#         if not props:
#             return "I did not find any properties relevant to this email."
#         if len(props) == 1:
#             return f"The relevant property is: {props[0]['name']}."
#         prop_list = "; ".join([prop['name'] for prop in props])
#         return f"The relevant properties are: {prop_list}."

#     def result(step_ctx: dict):
#         relevant_properties = find_relevant_properties(
#             email_dump_without_attachments=email.dump(dump_attachments=False),
#             properties=step_ctx["find_properties_step"]["properties"]
#         )
#         return {
#             "properties": relevant_properties["result"],
#             "summary": relevant_properties["summary"]
#         }

#     return Step(
#         id="find_relevant_properties_step",
#         name="Find Relevant Properties to Email",
#         function=lambda step_ctx: result(step_ctx),
#         start_message=start_message,
#         end_message=end_message,
#         message_queue=message_queue
#     )


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


def find_submission_wide_information(email_dump: str) -> dict:
    result = llm.chat(
        message=f"============= Context ============= \n{email_dump}",
        system_message=read_system_prompt("extract_isr_dates.md"),
        model=Model.gpt_4_1,
        response_format=ISRDates
    )
    result = result.model_dump()
    submission_data = {}
    for field in ("quotation_date", "inception_date"):
        entry = result.get(field, {}) or {}
        date_str = entry.get("value")
        source_str = entry.get("source")

        # Parse into a datetime if present
        parsed_date = string_to_datetime(date_str) if date_str else None

        submission_data[field] = {
            "value": parsed_date,
            "source": source_str
        }

    return submission_data


def find_submission_wide_information_step(email: Email) -> Step:
    def start_message(_):
        return (
            "I am gathering all submission-wide details from the email and any attachments."
        )

    def end_message(step_result, _):
        info = step_result.get("submission_info", {})
        if not info:
            return "I did not find any submission-wide information in the email or attachments."
        lines = "\n".join(f"- {key}: {value}" for key, value in info.items())
        return f"I extracted the following submission-wide details:\n{lines}"

    return Step(
        id="find_submission_wide_information_step",
        name="Find Submission-Wide Information",
        function=lambda _: {
            "submission_info": find_submission_wide_information(email.dump())
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


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


def extract_structured_date_per_property(relevant_properties: List[dict], email_dump: str) -> dict:
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

    return Step(
        id="extract_structured_data_per_property_step",
        name="Extract Structured Data Per Property",
        function=lambda step_ctx: {
            "structured_data_per_property": extract_structured_date_per_property(
                step_ctx["find_relevant_properties_step"]["properties"], email.dump())
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def aggregate_data_step() -> Step:
    def start_message(_):
        return "I am aggregating submission-wide information with structured data for each property."

    def end_message(step_result, _):
        submission_info = step_result.get("submission_info", {})
        property_data = step_result.get("structured_data_per_property", {})

        if not submission_info and not property_data:
            return "No data was available to aggregate."

        parts = []

        if submission_info:
            parts.append("Submission-wide information:")
            for key, value in submission_info.items():
                parts.append(f"- {key}: {value}")

        if property_data:
            parts.append("\nStructured data per property:")
            for prop, data in property_data.items():
                parts.append(f"{prop}:\n{json_dump(data)}")

        joined = "\n".join(parts)
        return f"Aggregation complete. Combined data:\n{joined}"

    return Step(
        id="aggregate_data_step",
        name="Aggregate Data",
        function=lambda step_ctx: {
            "submission_info": step_ctx["find_submission_wide_information_step"]["submission_info"],
            "structured_data_per_property": step_ctx["extract_structured_data_per_property_step"]["structured_data_per_property"],
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def clean_data_step() -> Step:
    def start_message(_):
        return (
            "I am cleaning and normalizing the submission-wide information "
            "and structured data for each property."
        )

    def end_message(step_result, _):
        cleaned_props = step_result.get("structured_data_per_property", {})
        if not cleaned_props:
            return "No property data required cleaning or normalization."
        count = len(cleaned_props)
        if count == 1:
            prop_name = next(iter(cleaned_props))
            return (
                f"Cleaned and normalized data for 1 property: {prop_name}."
            )
        prop_list = "; ".join(cleaned_props.keys())
        return (
            f"Cleaned and normalized data for {count} properties: {prop_list}."
        )

    return Step(
        id="clean_data_step",
        name="Clean Data",
        function=lambda ctx: {
            "submission_info": ctx["find_submission_wide_information_step"]["submission_info"],
            "structured_data_per_property": clean_properties(
                relevant_properties=ctx["find_relevant_properties_step"]["properties"],
                structured_data_per_property=ctx["extract_structured_data_per_property_step"]["structured_data_per_property"],
            )
        },
        # start_message=start_message,
        # end_message=end_message,
        message_queue=message_queue
    )


with open(f"./data/risk_matrix.json", "r") as f:
    risk_matrix = json.load(f)


def apply_appetite_matrix(property: dict, risk_matrix: dict) -> dict:
    industry_type = property["industry_type"]

    main_category = industry_type["main_category"]
    sub_category = industry_type["sub_category"]

    established_and_financially_stable = property["established_and_financially_stable"]["value"]
    purpose_built_premises = property["purpose_built_premises"]["value"]
    sprinkler_protected = property["fire_protection"]["sprinklers"]["value"]
    proactively_risk_managed_and_tested_BCP = property[
        "proactively_risk_managed_and_tested_BCP"]["value"]
    engaged_in_the_legal_and_regulatory_landscape_of_their_markets = property[
        "engaged_in_the_legal_and_regulatory_landscape_of_their_markets"]["value"]

    risk_values = [
        established_and_financially_stable,
        purpose_built_premises,
        sprinkler_protected,
        proactively_risk_managed_and_tested_BCP,
        engaged_in_the_legal_and_regulatory_landscape_of_their_markets
    ]

    risk_values = [e if e is not None else False for e in risk_values]

    required_criteria_idx = risk_matrix[main_category][sub_category]
    minimum_criteria_met = True
    missing_categories = []
    for i in required_criteria_idx:
        if risk_values[i] == False:
            minimum_criteria_met = False
            missing_categories.append(i)

    return {
        "missing_categories": missing_categories,
        "minimum_criteria_met": minimum_criteria_met
    }


def apply_appetite_matrix_to_all_properties(properties: dict, risk_matrix: dict) -> dict:
    result = {
        "in_appetite_properties": [],
        "out_of_appetite_properties": []
    }
    for property_name, property_data in properties.items():
        appetite_result = apply_appetite_matrix(property_data, risk_matrix)
        if appetite_result["minimum_criteria_met"]:
            result["in_appetite_properties"].append({
                "name": property_name,
            })
        else:
            result["out_of_appetite_properties"].append({
                "name": property_name,
                "reason": appetite_result["missing_categories"]
            })

    return result


def apply_appetite_matrix_step() -> Step:
    def start_message(_):
        return (
            "I am evaluating each property against Zurich’s appetite matrix and underwriting rules."
        )

    def end_message(step_result, _):
        evaluation = step_result.get("appetite_evaluation", {})
        in_appetite = evaluation.get("in_appetite_properties", [])
        out_of_appetite = evaluation.get("out_of_appetite_properties", [])

        if not in_appetite and not out_of_appetite:
            return "No appetite evaluation results were produced."

        parts = []
        if in_appetite:
            names = ", ".join(item["name"] for item in in_appetite)
            parts.append(f"Properties within appetite: {names}.")
        if out_of_appetite:
            details = "; ".join(
                f"{item['name']} (missing criteria indices: {item['reason']})"
                for item in out_of_appetite
            )
            parts.append(f"Properties outside appetite: {details}.")

        joined = "\n".join(parts)
        return f"Appetite matrix evaluation complete:\n{joined}"

    return Step(
        id="apply_appetite_matrix_step",
        name="Apply Appetite Matrix Step",
        function=lambda ctx: {
            "appetite_evaluation": apply_appetite_matrix_to_all_properties(
                properties=ctx["clean_data_step"]["structured_data_per_property"],
                risk_matrix=risk_matrix
            )
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def check_quick_decline_rules_data(submission: dict) -> dict:
    missing_values = []

    inception_date = submission["submission_info"]["inception_date"]
    if inception_date is None:
        missing_values.append(
            "The inception date of the isr submission is missing"
        )

    quotation_date = submission["submission_info"]["quotation_date"]
    if quotation_date is None:
        missing_values.append(
            "The quotation date of the isr submission is missing"
        )

    for property_name, property_data in submission["structured_data_per_property"].items():
        if property_data["total_declared_value"]["value"] is None:
            missing_values.append(
                f"The total declared value of {property_name} is missing"
            )

        wood = property_data["construction_materials"]["wood"]["value"]
        if wood is None:
            missing_values.append(
                f"The information of the construction material woord is missing"
            )

    return missing_values


def check_quick_decline_rules_data_step() -> Step:
    def start_message(_):
        return "I am verifying that all required data for quick decline rules is present."

    def end_message(step_result, _):
        missing = step_result.get("missing_values", [])
        if not missing:
            return "All data required for quick decline rules is available."
        missing_list = "; ".join(missing)
        return f"The following data required for quick decline rules is missing: {missing_list}."

    return Step(
        id="check_quick_decline_rules_data",
        name="Check Quick Decline Rules Data",
        function=lambda step_ctx: {
            "missing_values": check_quick_decline_rules_data(
                step_ctx["clean_data_step"]
            )
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


def apply_quick_decline_rules(submission: Dict) -> List[str]:
    """
    Evaluate quick-decline rules and collect all applicable decline reasons.
    Returns an empty list if no rules trigger.
    """
    reasons: List[str] = []

    # Rule 1: Backdating - Inception date is before quote date
    try:
        inception_date: datetime = submission["policy_info"]["inception_date"]
        quote_date: datetime = submission["policy_info"]["quotation_date"]
        if inception_date < quote_date:
            reasons.append(
                "Decline: The policy inception date is before the quote date."
            )
    except Exception:
        # Missing or unparsable dates => skip this rule
        pass

    # Rule 2: Total Declared Values < minimum
    try:
        declared_total = sum(
            prop["total_declared_value"]["value"]
            for prop in submission["properties"].values()
        )
        if declared_total < config.ISR_SETTINGS.MAX_TOTAL_AMOUNT:
            reasons.append(
                "Decline: Combined Declared Values for Sections 1 & 2 are below the required minimum."
            )
    except Exception:
        pass

    # Rules 3 & 4 only for single-location submissions
    try:
        if len(submission["properties"]) == 1:
            # Get the sole property data
            prop_name, prop_data = next(iter(submission["properties"].items()))
            post_code = prop_data.get("postal_code")
            # Rule 3: Knockout postcode
            if post_code in config.ISR_SETTINGS.KNOCKOUT_POSTCODES:
                reasons.append(
                    "Decline: Property postcode is in a knockout location outside appetite."
                )
            # Rule 4: Wood construction
            if prop_data["construction_materials"]["wood"]["value"]:
                reasons.append(
                    "Decline: Property construction type is wood, which is outside appetite."
                )
    except Exception:
        pass

    return reasons

# apply_quick_decline_rules(submission)


def get_context_pipeline(email: Email):
    return Sequence([
        find_customer_step(email),
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
        create_new_submission_step(),
        find_submission_wide_information_step(email),
        extract_structured_data_per_property_step(email),
        aggregate_data_step(),
        clean_data_step(),
        apply_appetite_matrix_step(),
        check_quick_decline_rules_data_step(),
        AbortIf(
            cond=lambda step_ctx: len(
                step_ctx["check_quick_decline_rules_data"]["missing_values"]) > 0,
            message=lambda step_ctx: (
                "Cannot evaluate quick-decline rules, for the following reasons: "
                f"{', '.join(step_ctx['check_quick_decline_rules_data']['missing_values'])}. "
                "Please provide these before underwriting can continue."
            )
        ),
        InspectNode()
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
    context_pipeline = get_context_pipeline(email)

    from agent.step_ctx import step_ctx

    step_ctx = {}
    try:
        result = context_pipeline.execute(step_ctx)

        # TODO: classify email: request, question, additional info
        # execute the appropriate pipeline

        print(json.dumps(agent_ctx, indent=2))
        print("\n\n")

    except StopExecution as e:
        message_queue.push(Message(e.message))

    except Exception as e:
        print("Error whilst executing pipeline")
        print_exc()

    finally:
        print(json.dumps(agent_ctx, indent=2))
