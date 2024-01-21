from enum import Enum

from checkin.root.utils.base_schemas import AbstractModel
from pydantic import EmailStr, conint
from typing import Optional, List, Union


class PaginatedQuery(AbstractModel):
    limit: conint(ge=0) = 10
    offset: conint(ge=0) = 0


class Installation(Enum):
    akure = "AKURE"
    ife = "IFE"
    island = "ISLAND"
    ikeja = "IKEJA"
    uk = "UK"
    moro = "MORO"
    yaba = "YABA"
    global_ = "GLOBAL"
    ibadan = "IBADAN"


class AkureTribe(Enum):
    ...


class IslandTribe(Enum):
    ...


class IkejaTribe(Enum):
    ...


class UKTribe(Enum):
    ...


class MoroTribe(Enum):
    ...


class YabaTribe(Enum):
    ...


class IbadanTribe(Enum):
    ...
