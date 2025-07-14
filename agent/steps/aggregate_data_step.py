from model.pipeline import Step
from model.messageQueue.instance import message_queue
from helpers import json_dump


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
