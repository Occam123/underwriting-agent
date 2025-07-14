from model.pipeline import Step
from model.messageQueue.instance import message_queue
import json


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
