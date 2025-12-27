import os

def get_env(var_name: str, default=None, required: bool = False):
    value = os.getenv(var_name, default)

    if required and value is None:
        raise EnvironmentError(f"Missing required env variable: {var_name}")

    return value


DATABASE_URL = get_env("DATABASE_URL", "sqlite:///db.sqlite3")
