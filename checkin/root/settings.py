from .utils.base_schemas import AbstractSettings
from pydantic.networks import PostgresDsn, RedisDsn
from pydantic import EmailStr


class Settings(AbstractSettings):
    postgres_url: PostgresDsn
    redis_url: RedisDsn
    jwt_secret_key: str
    ref_jwt_secret_key: str
    second_signer_key: str
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_from_name: str
    mail_port: int
    mail_server: str
