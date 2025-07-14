from typing import List, Dict, Any, Callable
import copy
from model.pipeline import Step
from model.messageQueue.instance import message_queue


def general_preprocess(field: dict) -> dict:
    if not field.get("source"):
        field["value"] = None
        field["source"] = None
    return field


def process_wood_field(field: dict) -> dict:
    if field.get("value") is None:
        field["value"] = False
        field["source"] = "Updated in process config"
    return field

# --- Field path utilities ---


def get_all_field_paths(d: Any, prefix: str = "") -> List[str]:
    """Recursively collects all variable paths in the dict or list."""
    paths = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_prefix = f"{prefix}/{k}" if prefix else k
            if isinstance(v, (dict, list)):
                paths.extend(get_all_field_paths(v, new_prefix))
            else:
                paths.append(new_prefix)
    elif isinstance(d, list):
        for item in d:
            new_prefix = f"{prefix}/[*]"
            paths.extend(get_all_field_paths(item, new_prefix))
    return paths


def get_property_path_name(field_path: str) -> str:
    """Extract the relevant property path name for process_config."""
    if "total_declared_value/value" in field_path:
        return "total_declared_value"
    if "total_declared_value/source" in field_path:
        return None
    if field_path.endswith("/value"):
        return field_path.rsplit("/value", 1)[0]
    return None

# --- Gather all relevant field paths ---


def collect_all_field_paths(
    relevant_properties: List[Dict[str, Any]],
    structured_data_per_property: Dict[str, Any]
) -> List[str]:
    all_paths = set()
    for prop in relevant_properties:
        name = prop["name"]
        data = structured_data_per_property[name]
        paths = get_all_field_paths(data)
        # only keep those that end in "value" and extract their parent path
        paths = [get_property_path_name(p)
                 for p in paths if p.endswith("/value")]
        paths = [p for p in paths if p]
        all_paths.update(paths)
    return list(all_paths)

# --- Build process config ---


def build_process_config(field_paths: List[str]) -> Dict[str, List[Callable[[dict], dict]]]:
    config: Dict[str, List[Callable[[dict], dict]]] = {}
    for path in field_paths:
        funcs = [general_preprocess]
        if "wood" in path:
            funcs.append(process_wood_field)
        config[path] = funcs
    return config

# --- Apply process config to a copy of the data ---


def apply_process_config(
    process_config: Dict[str, List[Callable[[dict], dict]]],
    structured_data_per_property: Dict[str, Any]
) -> Dict[str, Any]:
    # work on a deep copy
    data_copy = copy.deepcopy(structured_data_per_property)

    def get_nested(d: dict, keys: List[str]):
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return None
        return d

    def set_nested(d: dict, keys: List[str], value: Any):
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    for prop_name, prop_data in data_copy.items():
        for path, funcs in process_config.items():
            keys = path.split("/")
            target = get_nested(prop_data, keys)
            if isinstance(target, dict):
                for fn in funcs:
                    target = fn(target)
                set_nested(prop_data, keys, target)

    return data_copy

# --- Orchestrate cleaning pipeline ---


def clean_properties(
    relevant_properties: List[Dict[str, Any]],
    structured_data_per_property: Dict[str, Any]
) -> Dict[str, Any]:
    # 1. Collect paths
    field_paths = collect_all_field_paths(
        relevant_properties, structured_data_per_property)
    # 2. Build config
    process_config = build_process_config(field_paths)
    # 3. Apply and return cleaned copy
    return apply_process_config(process_config, structured_data_per_property)


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
