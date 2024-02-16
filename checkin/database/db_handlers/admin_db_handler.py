from checkin.database.orms.admin_orm import Admin as Admin_DB
from checkin.root.database import async_session
import logging
from checkin.schemas.auth_schemas import (
    AdminUser,
    AdminUserProfile,
    AdminUserUpdate,
)
from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError
from checkin.services.service_utils.exception_collection import (
    CreateError,
    DeleteError,
    DuplicateError,
    NotFound,
    UpdateError,
)
from uuid import UUID

LOGGER = logging.getLogger(__name__)


async def create_admin(admin_user: AdminUser) -> AdminUserProfile:
    async with async_session() as session:
        stmt = insert(Admin_DB).values(admin_user.model_dump()).returning(Admin_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError:
            LOGGER.error(f"duplicate record found for {admin_user.model_dump()}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error(f"create_admin failed for {admin_user.model_dump()}")
            await session.rollback()
            raise CreateError

        await session.commit()
        return AdminUserProfile(**result.as_dict())


async def get_admin(email: str):
    async with async_session() as session:
        result = (
            await session.execute(select(Admin_DB).filter(Admin_DB.email == email))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return AdminUserProfile(**result.as_dict())


async def get_admin_via_phone_number(phone_number: str):
    async with async_session() as session:
        result = (
            await session.execute(
                select(Admin_DB).where(Admin_DB.phone_number == phone_number)
            )
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return AdminUserProfile(**result.as_dict())


async def get_admin_profile(admin_uid: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(Admin_DB).where(Admin_DB.admin_uid == admin_uid)
            )
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return AdminUserProfile(**result.as_dict())


async def update_agent(admin_user_update: AdminUserUpdate, admin_uid: UUID):
    async with async_session() as session:
        stmt = (
            update(Admin_DB)
            .where(Admin_DB.admin_uid == admin_uid)
            .values(admin_user_update.model_dump(exclude_none=True, exclude_unset=True))
            .returning(Admin_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return AdminUserProfile(**result.as_dict())


async def delete_admin(admin_uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(Admin_DB).where(Admin_DB.admin_uid == admin_uid).returning(Admin_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise DeleteError

        await session.commit()
        return AdminUserProfile(**result.as_dict())
