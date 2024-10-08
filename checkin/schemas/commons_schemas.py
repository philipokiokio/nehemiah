from enum import Enum

from checkin.root.utils.base_schemas import AbstractModel
from pydantic import conint


class PaginatedQuery(AbstractModel):
    limit: conint(ge=0) = 10
    offset: conint(ge=0) = 0


class Installation(str, Enum):
    akure = "AKURE"
    ife = "IFE"
    island = "ISLAND"
    ikeja = "IKEJA"
    uk = "UK"
    birmingham = "BIRMINGHAM"
    yaba = "YABA"
    global_ = "GLOBAL"
    ibadan = "IBADAN"


class AkureTribe(Enum): ...


class IslandTribe(str, Enum):
    greater_lekki = "Greater Lekki"
    lekki = "Lekki"


class IkejaTribe(Enum): ...


class UKTribe(Enum): ...


class MoroTribe(Enum): ...


class YabaTribe(Enum): ...


class IbadanTribe(Enum): ...
