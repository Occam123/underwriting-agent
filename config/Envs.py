from typing import List
import os
from dotenv import load_dotenv


class Envs:
    def __init__(self, vars: List[str], path: str) -> None:
        self.vars = vars

        # Ensure absolute path to env file based on script location
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        load_dotenv(abs_path)

    def __getattr__(self, var: str) -> any:
        if var in self.vars:
            value = os.environ.get(var)
            if value is None:
                print(f"WARNING: The value of the environment variable {var} is None.")
            return value

        raise AttributeError(f"The environment variable {var} is not allowed or not set.")


env_file = "../envs/.env"  # relative to the file containing this script

envs = Envs(
    [
        "OPENAI_API_KEY",
        "MISTRAL_API_KEY",
        "AZURE_OCR_ENDPOINT",
        "AZURE_OCR_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY"
    ],
    path=env_file
)
