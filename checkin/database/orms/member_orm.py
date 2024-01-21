from sqlalchemy.dialects.postgresql import UUID
from checkin.root.utils.abstract_base import AbstractBase

from sqlalchemy import String, Column, Date, Boolean
from uuid import uuid4


class Members(AbstractBase):
    __tablename__ = "members"
    member_uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False)
    installation = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    tribe = Column(String, nullable=False)
    checkin_token = Column(String, nullable=True)
    is_first_time = Column(Boolean, nullable=False)


class Attendance(AbstractBase):
    __tablename__ = "attendance"
    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_uid = Column(UUID(as_uuid=True), index=True)
    date = Column(Date, nullable=False)
    sunday_service = Column(Boolean, nullable=False)
    global_gethsemane = Column(Boolean, nullable=False)
    midweek_service = Column(Boolean, nullable=False)
    is_guest = Column(Boolean, nullable=False)
    guest_installation = Column(String, nullable=True)
