from config.Envs import envs


class Config:
    __instance = None

    def __init__(self, config: dict) -> None:
        for key, value in config.items():
            if isinstance(value, dict):
                # Recursively wrap dictionaries
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Config).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __getitem__(self, key: str) -> any:
        return getattr(self, key)


config = Config({
    "OPENAI": {
        "API_KEY": envs.OPENAI_API_KEY,
    },
    "MISTRAL": {
        "API_KEY": envs.MISTRAL_API_KEY,
    },
    "AZURE": {
        "OCR": {
            "ENDPOINT": envs.AZURE_OCR_ENDPOINT,
            "KEY":  envs.AZURE_OCR_KEY
        },
    },
    "DATETIME": {
        "OUTPUT_FORMAT": "%d/%m/%Y"
    },
    "ISR_SETTINGS": {
        "MAX_TOTAL_AMOUNT": 5_000_000,
        "KNOCKOUT_POSTCODES": (2060, 3000, 4000)
    },
    "SUPABASE": {
        "URL": envs.SUPABASE_URL,
        "KEY": envs.SUPABASE_KEY,
        "SERVICE_ROLE_KEY": envs.SUPABASE_SERVICE_ROLE_KEY
    }
})
