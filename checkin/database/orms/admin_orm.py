from sqlalchemy import String, Column
from checkin.root.utils.abstract_base import AbstractBase
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Admin(AbstractBase):
    __tablename__ = "admin"
    admin_uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    installation = Column(String, nullable=False)
    admin_type = Column(String, nullable=False)


# INSTALLATION AKURE, IFE, ISLAND, IKEJA, UK,MORO, YABA, GLOBAL
