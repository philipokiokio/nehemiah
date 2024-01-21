from checkin.schemas.commons_schemas import Installation
from checkin.root.utils.base_schemas import AbstractModel
from pydantic import Field, constr, conlist, EmailStr
from datetime import date, datetime
from enum import Enum
from uuid import UUID
from typing import Optional


class AdminType(Enum):
    installation = "INSTALLATION"
    global_ = "GLOBAL"


class AgentInviteToken(AbstractModel):
    invite_token: constr(max_length=4, min_length=4)


class Password(AbstractModel):
    password: constr(
        min_length=6,
        pattern="^[A-Za-z0-9!@#$&*_+%-=]+$",
    )


class Login(Password):
    email: EmailStr


class AdminUser(Login):
    first_name: str
    last_name: str
    phone_number: constr(min_length=9)
    installation: Installation
    admin_type: AdminType


class AdminUserProfile(AdminUser):
    admin_uid: UUID
    # excluding password
    password: str = Field(exclude=True)
    email: EmailStr = Field(exclude=True)


class AdminUserUpdate(AbstractModel):
    # TODO: Use a smarter method to make all fields optional
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[constr(max_length=11, min_length=9)] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    company: Optional[str] = None
    job_role: Optional[str] = None


class TokenData(AbstractModel):
    admin_uid: UUID


class AdminProfile(AbstractModel):
    agent_uid: UUID
    email: EmailStr


class UserAccessToken(AbstractModel):
    access_token: str
    refresh_token: str
