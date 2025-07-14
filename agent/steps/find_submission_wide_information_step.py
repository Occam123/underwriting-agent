from typing import List
from model.Email import Email
from model.pipeline import Step
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.ISRDates import ISRDates
from model.messageQueue.instance import message_queue

from helpers import string_to_datetime


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
