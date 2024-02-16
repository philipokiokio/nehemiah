from checkin.root.utils.base_schemas import AbstractModel
from typing import Optional, List, Union

from uuid import UUID
from pydantic import constr, EmailStr
from datetime import datetime
from checkin.schemas.commons_schemas import (
    IslandTribe,
    IkejaTribe,
    MoroTribe,
    IbadanTribe,
    UKTribe,
    YabaTribe,
    Installation,
)
from datetime import date, datetime


class Member(AbstractModel):
    first_name: str
    last_name: str


Date = date
PHONE_NUMBER = constr(max_length=15, min_length=11)


class NewMember(Member):
    email: EmailStr
    phone_number: PHONE_NUMBER
    is_first_time: bool = True
    tribe: Union[IslandTribe, IkejaTribe, MoroTribe, IbadanTribe, UKTribe, YabaTribe]


class MemberProfile(NewMember):
    checkin_token: str
    member_uid: UUID
    installation: Installation
    date_created_utc: datetime


class MemberUpdate(AbstractModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[PHONE_NUMBER] = None
    tribe_area: Optional[
        Union[IslandTribe, IkejaTribe, MoroTribe, IbadanTribe, UKTribe, YabaTribe]
    ] = None
    is_first_time: Optional[bool] = None


class Attendance(AbstractModel):
    member_uid: UUID
    date: Date
    sunday_service: bool
    global_gethsemane: bool
    midweek_service: bool
    is_guest: bool
    guest_installation: Optional[str] = None


class AttendanceUpdate(AbstractModel):
    date: Optional[Date] = None
    sunday_service: Optional[bool] = None
    midweek_service: Optional[bool] = None
    global_gethesmane: Optional[bool] = None


class AttendanceProfile(Attendance):
    uid: UUID
    date_created_utc: datetime


class PaginatedMemberAttendanceProfile(AbstractModel):
    result_set: list[AttendanceProfile] = []
    result_size: int = 0


class MemberExtendedProfile(MemberProfile):
    attendance: list[AttendanceProfile]


class PaginatedMemberProfile(AbstractModel):
    result_set: List[MemberExtendedProfile] = []
    result_size: int = 0


class AdminMemberStatistics(AbstractModel):
    total_number_members: int = 0
    total_number_first_timers: int = 0
    total_number_on_sunday: int = 0
    total_number_global_gethsemane: int = 0
    total_number_local_gethsemane: int = 0
