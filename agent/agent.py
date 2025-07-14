from typing import List, Dict
from traceback import print_exc
import json
from model.Email import Email
from model.pipeline import Sequence, Step, AbortIf
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.messageQueue.MessageQueue import Message
from helpers import json_dump
from exceptions import StopExecution
from model.messageQueue.instance import message_queue
from config.Config import config
from datetime import datetime

from agent.steps.find_properties_step import find_properties_step
from agent.steps.find_relevant_properties_step import find_relevant_properties_step
from agent.steps.find_customer_step import find_customer_step
from agent.steps.get_customer_context_step import get_customer_context_step
from agent.steps.create_new_submission_step import create_new_submission_step
from agent.steps.find_submission_wide_information_step import find_submission_wide_information_step
from agent.steps.extract_structured_data_per_property_step import extract_structured_data_per_property_step
from agent.steps.aggregate_data_step import aggregate_data_step
from agent.steps.clean_data_step import clean_data_step
from agent.steps.apply_appetite_matrix_step import apply_appetite_matrix_step
from agent.steps.check_quick_decline_rules_data_step import check_quick_decline_rules_data_step

AgentContext = dict

agent_ctx: AgentContext = {
}


def apply_quick_decline_rules(submission: Dict) -> Dict[str, List[str]]:
    """
    Evaluate quick-decline rules and collect:
      - submission_reasons: reasons that apply to the entire submission
      - property_reasons: reasons that apply to individual properties
    """
    submission_reasons: List[str] = []
    property_reasons: Dict[str, List[str]] = {}

    # Rule 1: Backdating — Inception before quote date
    inception_date: datetime = submission["submission_info"]["inception_date"]["value"]
    quote_date: datetime = submission["submission_info"]["quotation_date"]["value"]

    try:
        if inception_date < quote_date:
            submission_reasons.append(
                "Decline: The policy inception date is before the quote date."
            )
    except Exception as e:
        pass

    # Rule 2: Total Declared Values below minimum
    declared_total = sum(
        prop["total_declared_value"]["value"]
        for prop in submission["structured_data_per_property"].values()
    )
    try:
        if declared_total < config.ISR_SETTINGS.MAX_TOTAL_AMOUNT:
            submission_reasons.append(
                "Decline: Combined Declared Values for Sections 1 & 2 are below the required minimum."
            )
    except Exception as e:
        pass

    try:
        # Rules 3 & 4: apply per-property (only if one property, but can generalize)
        for prop_name, prop_data in submission["structured_data_per_property"].items():
            reasons: List[str] = []
            # Rule 3: Knockout postcode
            post_code = prop_data.get("postal_code")
            if post_code in config.ISR_SETTINGS.KNOCKOUT_POSTCODES:
                reasons.append(
                    "Decline: Postcode is in a knockout location outside appetite."
                )
            # Rule 4: Wood construction
            if prop_data["construction_materials"]["wood"]["value"]:
                reasons.append(
                    "Decline: Construction type is wood, which is outside appetite."
                )
            if reasons:
                property_reasons[prop_name] = reasons
    except Exception as e:
        pass

    return {
        "submission_reasons": submission_reasons,
        "property_reasons": property_reasons
    }


def apply_quick_decline_rules_step() -> Step:
    def start_message(_):
        return "I am evaluating the submission against quick-decline rules."

    def end_message(step_result, _):
        reasons = step_result.get("decline_reasons", [])
        if not reasons:
            return "No quick-decline rules were triggered."
        formatted = "\n".join(f"- {reason}" for reason in reasons)
        return f"The following quick-decline reasons were identified:\n{formatted}"

    return Step(
        id="apply_quick_decline_rules_step",
        name="Apply Quick-Decline Rules",
        function=lambda step_ctx: apply_quick_decline_rules(
            step_ctx["clean_data_step"]),
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )


appetite_matrix_map = {
    0: "Established and financially stable",
    1: "Purpose-built premises",
    2: "Sprinkler protected",
    3: "Proactively risk managed and tested BCP",
    4: "Engaged in the legal & regulatory landscape of their markets"
}


def assessing_submission_for_underwriting(
    relevant_properties: List[dict],
    quick_decline_rules: dict,
    out_of_appetite_properties: List[dict]
) -> dict:

    result = {
        "invalid_submission_wide_reasons": [],
        "properties": {
            "valid": [],
            "invalid": {}
        }
    }

    invalid_properties = set()

    for property in out_of_appetite_properties:
        property_name = property["name"]
        reasons = property["reason"]
        reasons = [
            f"The property is not {appetite_matrix_map[i]}" for i in reasons]

        result["properties"]["invalid"][property_name] = {
            "out_of_appetite": reasons
        }
        invalid_properties.add(property_name)

    for property_name, decline_reasons in quick_decline_rules["property_reasons"].items():
        if property_name in result["invalid"]:
            result["properties"]["invalid"][property_name]["quick_decline_reasons"] = decline_reasons
        else:
            result["properties"]["invalid"][property_name] = {
                "quick_decline_reasons": decline_reasons
            }
        invalid_properties.add(property_name)

    for property in relevant_properties:
        property_name = property["name"]
        if not property_name in invalid_properties:
            result["properties"]["valid"].append(property_name)

    result["invalid_submission_wide_reasons"] = quick_decline_rules["submission_reasons"]

    return result


def assess_submission_for_underwriting_step() -> Step:
    return Step(
        id="assess_submission_for_underwriting_step",
        name="Assess Submission for Underwriting",
        function=lambda step_ctx: assessing_submission_for_underwriting(
            step_ctx["find_relevant_properties_step"]["properties"],
            quick_decline_rules=step_ctx["apply_quick_decline_rules_step"],
            out_of_appetite_properties=step_ctx["apply_appetite_matrix_step"][
                "appetite_evaluation"]["out_of_appetite_properties"]
        ),
        message_queue=message_queue
    )


def create_submission_quoting(valid_property_names: List[dict], submission: dict) -> dict:
    def create_quote(property: dict) -> float:
        fake_quote = 10000000
        return fake_quote

    quote_per_property = {}
    for property_name in valid_property_names:
        quote = create_quote(
            submission["structured_data_per_property"][property_name])
        quote_per_property[property_name] = quote

    return quote_per_property


def create_submission_quoting_step() -> Step:
    return Step(
        id="create_submission_quoting_step",
        name="Create Submission Quoting",
        function=lambda step_ctx: {
            "quotes": create_submission_quoting(
                valid_property_names=step_ctx["assess_submission_for_underwriting_step"]["properties"]["valid"],
                submission=step_ctx["clean_data_step"]
            )
        },
        message_queue=message_queue
    )


def write_final_message(email: Email, submission_assessment: dict, quotes: dict) -> None:
    context = f"========== Email ==========\n{email.dump(dump_attachments=False)}\n========== Submission assessment ==========\n{json_dump(submission_assessment)}========== Quotes ==========\n{quotes}"

    result = llm.chat(
        message=context,
        system_message=read_system_prompt("write_final_email.md"),
        model=Model.o4_mini,
        reasoning={
            "effort": "medium",
            "summary": "detailed"
        }
    )
    return result["result"]


def write_final_message_step(email: Email) -> Step:
    """
    A pipeline Step that generates the final email.
    - No start_message.
    - Uses the output of the underwriting assessment and quoting steps.
    - end_message simply returns the LLM’s result as the final message.
    """
    return Step(
        id="write_final_message_step",
        name="Write Final Underwriting Email",
        function=lambda ctx: write_final_message(
            email,
            ctx["assess_submission_for_underwriting_step"],
            ctx["create_submission_quoting_step"]["quotes"]
        ),
        start_message="I will write a response email to the submission request",
        end_message=lambda result, _: result,
        message_queue=message_queue
    )


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
        # aggregate_data_step(),
        # clean_data_step(),
        # apply_appetite_matrix_step(),
        # check_quick_decline_rules_data_step(),
        # AbortIf(
        #     cond=lambda step_ctx: len(
        #         step_ctx["check_quick_decline_rules_data"]["missing_values"]) > 0,
        #     message=lambda step_ctx: (
        #         "Cannot evaluate quick-decline rules, for the following reasons: "
        #         f"{', '.join(step_ctx['check_quick_decline_rules_data']['missing_values'])}. "
        #         "Please provide these before underwriting can continue."
        #     )
        # ),
        # apply_quick_decline_rules_step(),
        # AbortIf(
        #     cond=lambda step_ctx: not step_ctx["find_relevant_properties_step"]["properties"],
        #     message="No relevant properties could be identified for this email."
        # ),
        # assess_submission_for_underwriting_step(),
        # create_submission_quoting_step(),
        # write_final_message_step(email)
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

    # print(email.dump())
    # print("\n\n\n")

    step_ctx = {}
    try:
        result = await context_pipeline.execute(step_ctx)

        # print(json_dump(result))
        # print("\n\n")

        # TODO: classify email: request, question, additional info
        # execute the appropriate pipeline

        # print(json_dump(agent_ctx))
        # print("\n\n")

    except StopExecution as e:
        message_queue.push(Message(e.message))

    except Exception as e:
        print("Error whilst executing pipeline")
        print_exc()
        print("================= step ctx ================= ")
        print(json_dump(step_ctx))
        print("\n\n")
        print("================= agent ctx ================= ")
        print(json_dump(agent_ctx))

    finally:
        pass
        # print("================= step ctx ================= ")
        # print(json_dump(step_ctx))
        # print("\n\n")
        # print("================= agent ctx ================= ")
        # print(json_dump(agent_ctx))
