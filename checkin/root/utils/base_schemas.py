from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class AbstractSettings(BaseSettings):
    class Config:
        env_file = ".env"


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
