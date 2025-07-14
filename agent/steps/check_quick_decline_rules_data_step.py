from model.pipeline import Step
from model.messageQueue.instance import message_queue


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
