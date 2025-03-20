from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = False
    model_config = SettingsConfigDict(
        env_prefix="TEST_",
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="PROD_",
    )


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="DEV_",
    )


@lru_cache()
def get_config(env_state: Optional[str]) -> BaseConfig:
    config_map = {
        "test": TestConfig,
        "prod": ProdConfig
    }
    return config_map.get(env_state, DevConfig)()


config = get_config(BaseConfig().ENV_STATE)