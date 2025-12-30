import os

def get_env(var_name: str, default=None, required: bool = False):
    value = os.getenv(var_name, default)

    if required and value is None:
        raise EnvironmentError(f"Missing required env variable: {var_name}")

    return value


POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "PASSWORD")
POSTGRES_USER = get_env("POSTGRES_USER", "USER")
DATABASE_URL = get_env("DATABASE_URL", f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/APP")
