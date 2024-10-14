from sqlalchemy import insert, select, update, delete, and_, func
from sqlalchemy.exc import IntegrityError
from checkin.services.service_utils.exception_collection import (
    CreateError,
    DeleteError,
    DuplicateError,
    NotFound,
    UpdateError,
)
from checkin.schemas.member_schemas import (
    AdminMemberStatistics,
    Attendance,
    AttendanceProfile,
    AttendanceUpdate,
    MemberExtendedProfile,
    NewMember,
    MemberProfile,
    Installation,
    MemberUpdate,
    PaginatedMemberAttendanceProfile,
    PaginatedMemberProfile,
)
from uuid import UUID
from checkin.root.database import async_session
import logging
from checkin.database.orms.member_orm import Members as MemberDB
from checkin.database.orms.member_orm import Attendance as AttendanceDB
from datetime import date
from itsdangerous.url_safe import URLSafeSerializer

LOGGER = logging.getLogger(__file__)


s = URLSafeSerializer("neheimah")


def checkin_token_gen(member_uid: str):
    return s.dumps(member_uid)


async def create_new_member(new_member: NewMember, installation: Installation):
    async with async_session() as session:
        stmt = (
            insert(MemberDB)
            .values(
                **new_member.model_dump(),
                installation=installation.value,
                is_first_time=True,
            )
            .returning(MemberDB)
        )
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()

        except IntegrityError:
            LOGGER.exception(IntegrityError)
            LOGGER.error(f"duplicate record found for {new_member.model_dump()}")
            await session.rollback()
            raise DuplicateError

        if not result:
            LOGGER.error(f"create new member failed, for {new_member.model_dump()}")
            session.rollback()
            raise CreateError

        result.checkin_token = checkin_token_gen(member_uid=str(result.member_uid))

        await session.commit()
        return MemberExtendedProfile(**result.as_dict(), attendance=[])


async def get_member(member_uid: UUID):
    async with async_session() as session:
        stmt = select(MemberDB).where(MemberDB.member_uid == member_uid)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"no record was found for member: {member_uid}")

            raise NotFound

        # attendance
        member_attendance = await get_member_attendance_records(
            member_uid=result.member_uid
        )

        return MemberExtendedProfile(
            **result.as_dict(), attendance=member_attendance.result_set
        )


async def get_member_via_names(first_name: UUID, last_name: UUID, **kwargs):
    async with async_session() as session:
        stmt = select(MemberDB).where(
            and_(
                MemberDB.first_name.icontains(first_name),
                MemberDB.last_name.icontains(last_name),
            )
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"no record was found for: {first_name}, and {last_name}")

            raise NotFound
        # attendance
        member_attendance = await get_member_attendance_records(
            member_uid=result.member_uid
        )
        return MemberExtendedProfile(
            **result.as_dict(), attendance=member_attendance.result_set
        )


async def get_member_via_mail(email: str):
    async with async_session() as session:
        stmt = select(MemberDB).filter(MemberDB.email == email)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"no record was found for: {email}")

            raise NotFound
        # attendance
        member_attendance = await get_member_attendance_records(
            member_uid=result.member_uid
        )
        return MemberExtendedProfile(
            **result.as_dict(), attendance=member_attendance.result_set
        )


async def get_member_via_checkin_token(checkin_token: str, **kwargs):
    async with async_session() as session:
        stmt = select(MemberDB).filter(MemberDB.checkin_token == checkin_token)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"no record was found for: {checkin_token}")

            raise NotFound
        # attendance
        member_attendance = await get_member_attendance_records(
            member_uid=result.member_uid
        )
        return MemberExtendedProfile(
            **result.as_dict(), attendance=member_attendance.result_set
        )


async def get_installation_members(installation: Installation, **kwargs):
    limit = kwargs.get("limit", 10)
    offset = kwargs.get("offset", 0)

    filter_case = [MemberDB.installation == installation]
    if installation == Installation.global_.value:
        filter_case = []
    async with async_session() as session:
        stmt = select(MemberDB).filter(and_(*filter_case))
        stmt.offset(offset=offset).limit(limit=limit)
        result = (await session.execute(statement=stmt)).scalars().all()
        match_size = (
            await session.execute(
                select(func.count(MemberDB.member_uid)).filter(*filter_case)
            )
        ).scalar()

        if not result:
            return PaginatedMemberProfile()

        pagninated_member_profile = PaginatedMemberProfile(result_size=match_size)

        for x in result:
            member_attendance = await get_member_attendance_records(
                member_uid=x.member_uid
            )
            pagninated_member_profile.result_set.append(
                MemberExtendedProfile(
                    **x.as_dict(), attendance=member_attendance.result_set
                )
            )

        return pagninated_member_profile


async def update_member(member_uid: UUID, member_update: MemberUpdate):
    update_member_dict = member_update.model_dump(exclude_none=True, exclude_unset=True)

    async with async_session() as session:
        stmt = (
            update(MemberDB)
            .filter(MemberDB.member_uid == member_uid)
            .values(**update_member_dict)
            .returning(MemberDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return MemberProfile(**result.as_dict())


async def delete_member(member_uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(MemberDB)
            .filter(MemberDB.member_uid == member_uid)
            .returning(MemberDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise DeleteError

        await delete_member_attendance_record(member_uid=member_uid)
        await session.commit()

        return MemberProfile(**result.as_dict())


######################## Attendance ########################################################


async def create_attendance_record(attendance: Attendance):
    async with async_session() as session:
        stmt = (
            insert(AttendanceDB)
            .values(**attendance.model_dump())
            .returning(AttendanceDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            LOGGER.error(f"attendance was not saved {attendance.model_dump()}")
            raise CreateError

        await session.commit()

        return AttendanceProfile(**result.as_dict())


async def get_member_attendance_records(member_uid: UUID):
    async with async_session() as session:
        stmt = select(AttendanceDB).filter(AttendanceDB.member_uid == member_uid)

        result = (await session.execute(statement=stmt)).scalars().all()

        match_size = (
            await session.execute(
                select(func.count(AttendanceDB.member_uid)).filter(
                    AttendanceDB.member_uid == member_uid
                )
            )
        ).scalar()

        if not result:
            return PaginatedMemberAttendanceProfile()

        return PaginatedMemberAttendanceProfile(
            result_set=[AttendanceProfile(**x.as_dict()) for x in result],
            result_size=match_size,
        )


async def get_todays_attendance(member_uid: UUID, date_: date):
    async with async_session() as session:
        stmt = select(AttendanceDB).filter(
            AttendanceDB.member_uid == member_uid,
            AttendanceDB.date == date_,
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if result is None:
            LOGGER.error(
                f"there is no attendance record for member with member_uid:{member_uid}, for date: {date_}"
            )
            raise NotFound

        return [AttendanceProfile(**x.as_dict()) for x in result]


async def get_member_attendance_record(member_uid: UUID, uid: UUID):
    async with async_session() as session:
        stmt = select(AttendanceDB).filter(
            AttendanceDB.member_uid == member_uid, AttendanceDB.uid == uid
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(
                f"attendance for member: {member_uid} and uid: {uid}  not found"
            )
            raise NotFound

        return AttendanceProfile(**result.as_dict())


async def get_member_attendance_record_via_uid(uid: UUID):
    async with async_session() as session:
        stmt = select(AttendanceDB).filter(AttendanceDB.uid == uid)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(f"attendance for uid: {uid}  not found")
            raise NotFound

        return AttendanceProfile(**result.as_dict())


async def update_member_attendance_record(
    member_uid: UUID, uid: UUID, attendance_update: AttendanceUpdate
):
    async with async_session() as session:
        stmt = (
            update(AttendanceDB)
            .filter(AttendanceDB.member_uid == member_uid, AttendanceDB.uid == uid)
            .values(
                **attendance_update.model_dump(exclude_none=True, exclude_unset=True)
            )
            .returning(AttendanceDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            LOGGER.error(
                f"attendance for member: {member_uid} and uid: {uid} failed to update"
            )
            raise DeleteError

        await session.commit()

        return AttendanceProfile(**result.as_dict())


async def delete_attendance_record(uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(AttendanceDB).filter(AttendanceDB.uid == uid).returning(AttendanceDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            LOGGER.error(f"attendance for uid: {uid} failed to delete")
            raise DeleteError

        await session.commit()

        return AttendanceProfile(**result.as_dict())


async def delete_member_attendance_record(member_uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(AttendanceDB)
            .filter(AttendanceDB.member_uid == member_uid)
            .returning(AttendanceDB)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            await session.rollback()
            LOGGER.error(f"attendance for member_uid: {member_uid} failed to delete")
            raise DeleteError

        await session.commit()

        return


# ADMIN DATA GENERATION
# Total Number of Members
# Total Number of First timers (bound by installation/global role)
# Total Number At Church On Sunday
# Total Number At Church for Gethsemane
async def member_attendance_statistics(
    installation: Installation, member_uids: list[UUID] = None
):
    filter_case = [AttendanceDB.member_uid.in_(member_uids)]
    if member_uids is None:
        filter_case = []
    async with async_session() as session:
        global_gethsemane_stmt = select(
            (func.count(AttendanceDB.global_gethsemane))
        ).filter(and_(*filter_case, AttendanceDB.global_gethsemane == True))

        total_number_on_sunday = select(
            (func.count(AttendanceDB.sunday_service))
        ).filter(and_(*filter_case, AttendanceDB.sunday_service == True))
        local_gethsemane = select((func.count(AttendanceDB.midweek_service))).filter(
            and_(*filter_case, AttendanceDB.midweek_service == True)
        )

        installqtion_filter_case = [MemberDB.installation == installation]
        if installation == Installation.global_:
            filter_case = []
        total_number_member = select((func.count(MemberDB.member_uid))).filter(
            and_(*installqtion_filter_case)
        )

        total_number_first_time = select((func.count(MemberDB.member_uid))).filter(
            and_(*installqtion_filter_case, MemberDB.is_first_time == True)
        )

        global_gethsemane_result = (
            await session.execute(statement=global_gethsemane_stmt)
        ).scalar()
        total_number_on_sunday_result = (
            await session.execute(statement=total_number_on_sunday)
        ).scalar()

        local_gethsemane_result = (
            await session.execute(statement=local_gethsemane)
        ).scalar()
        total_number_member_result = (
            await session.execute(statement=total_number_member)
        ).scalar()
        total_number_first_time_result = (
            await session.execute(statement=total_number_first_time)
        ).scalar()

        return AdminMemberStatistics(
            total_number_first_timers=total_number_first_time_result,
            total_number_global_gethsemane=global_gethsemane_result,
            total_number_local_gethsemane=local_gethsemane_result,
            total_number_on_sunday=total_number_on_sunday_result,
            total_number_members=total_number_member_result,
        )
