import os
import json
from json_default import json_default
from datetime import datetime
import dateparser
from typing import List, Tuple
import tiktoken
from sentence_transformers import SentenceTransformer
from config.Config import config

# --------------------- io ---------------------


def base_path() -> str:
    return "/Users/laurenswissels/Documents/Startup/code/agent-solution"


def read_system_prompt(filename: str) -> str:
    with open(f"{base_path()}/prompt/{filename}", "r") as f:
        system_prompt = f.read()
    return system_prompt

# -------------------------------------- datetime --------------------------------------


def string_to_datetime(datetime_string: str) -> datetime:
    try:
        # Normalize the input: strip whitespace and normalize unicode
        normalized_string = datetime_string.strip()

        # Use dateparser to flexibly parse nearly any date format
        parsed_datetime = dateparser.parse(
            normalized_string,
            settings={
                'PREFER_DAY_OF_MONTH': 'first',
                'DATE_ORDER': 'DMY',
                'TIMEZONE': 'UTC',
                'RETURN_AS_TIMEZONE_AWARE': False,
                'RELATIVE_BASE': datetime.now()
            },
            languages=['nl']  # Add more languages if needed
        )

        if parsed_datetime is None:
            raise Exception("Parse exception")

        return parsed_datetime

    except (TypeError, ValueError) as e:
        raise Exception(f"Error while converting string to datetime: {e}")


def datetime_to_string(datetime: datetime, format: str) -> str:
    try:
        return datetime.strftime(format)
    except (TypeError, ValueError) as e:
        raise Exception(f"Error while converting datetime to string: {e}")

# -------------------------------------- json --------------------------------------


def json_dump(obj: dict) -> str:
    # Fix: custom converter!
    return json.dumps(obj, indent=2, default=json_default)
