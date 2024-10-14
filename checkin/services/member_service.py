from checkin.schemas.commons_schemas import Installation
from checkin.schemas.member_schemas import (
    AttendanceProfile,
    Member,
    MemberExtendedProfile,
    MemberUpdate,
    NewMember,
    Attendance,
    AttendanceUpdate,
)
from uuid import UUID
import checkin.database.db_handlers.member_db_handler as member_db_handler
import logging
from fastapi import HTTPException, status
import checkin.services.service_error_enums as service_utils
from checkin.services.service_utils.exception_collection import (
    DeleteError,
    DuplicateError,
    NotFound,
    UpdateError,
)
import checkin.services.service_utils.attendance_utils as attendance_utils
from datetime import date

LOGGER = logging.getLogger(__file__)


async def create_first_time_member(new_member: NewMember, installation: Installation):
    try:
        await _get_member(
            first_name=new_member.first_name, last_name=new_member.last_name
        )
        raise HTTPException(**service_utils.ErrorEnum.member_found())
    except NotFound:
        try:
            member_profile = await member_db_handler.create_new_member(
                new_member=new_member, installation=installation
            )

            # create attendance
            attendance_profile = await create_attendance_record(
                member_uid=member_profile.member_uid,
                installation=member_profile.installation,
                member_installation=member_profile.installation,
            )
            return await __condinational_attendance_update(
                attendance_profile=attendance_profile, member_profile=member_profile
            )
        except DuplicateError as e:
            LOGGER.exception(e)
            LOGGER.error("agent duplicate found")
            raise HTTPException(**service_utils.ErrorEnum.member_found())


async def _get_member(first_name: str, last_name: str, **kwargs):
    try:
        return await member_db_handler.get_member_via_names(
            last_name=last_name, first_name=first_name
        )
    except NotFound:
        logging.error(
            f"There is no member with first_name: {first_name}, last_name: {last_name}"
        )
        raise NotFound


async def member_checkin_via_checkin_token(
    checkin_token: str, installation: Installation
):
    try:
        member_profile = await member_db_handler.get_member_via_checkin_token(
            checkin_token=checkin_token
        )

        await __update_to_member_status(member_profile=member_profile)

        attendance_profile = await create_attendance_record(
            member_uid=member_profile.member_uid,
            member_installation=member_profile.installation,
            installation=installation,
        )
        return await __condinational_attendance_update(
            attendance_profile=attendance_profile, member_profile=member_profile
        )
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="member not found",
        )


async def __get_member_via_names(first_name: str, last_name: str):
    try:
        return await _get_member(first_name=first_name, last_name=last_name)
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no member with name: {first_name} {last_name} is found",
        )


async def __update_to_member_status(member_profile: MemberExtendedProfile):
    if len(member_profile.attendance) >= 4:
        await member_db_handler.update_member(
            member_uid=member_profile.member_uid,
            member_update=MemberUpdate(is_first_time=False),
        )


async def __condinational_attendance_update(
    attendance_profile: AttendanceProfile, member_profile: MemberExtendedProfile
):
    if len(member_profile.attendance) == 0:
        member_profile.attendance.append(attendance_profile)

    elif attendance_profile[-1].uid != member_profile.attendance[-1].uid:
        member_profile.attendance.append(attendance_profile)

    return member_profile


async def member_checkin(member: Member, installation: Installation):
    member_profile = await __get_member_via_names(
        first_name=member.first_name, last_name=member.last_name
    )

    await __update_to_member_status(member_profile=member_profile)
    attendance_profile = await create_attendance_record(
        member_uid=member_profile.member_uid,
        member_installation=member_profile.installation,
        installation=installation,
    )
    return await __condinational_attendance_update(
        attendance_profile=attendance_profile, member_profile=member_profile
    )


async def create_attendance_record(
    member_uid: UUID, member_installation: Installation, installation: Installation
):
    today = attendance_utils.today()

    # check if record for today exist before creating a new record
    try:
        todays_attendance = await get_todays_attendance(
            member_uid=member_uid, date_=today
        )

        if member_installation != installation:

            raise HTTPException(status_code=400, detail="")

        return todays_attendance

    except HTTPException:
        is_guest = True
        guest_installation = installation
        if member_installation == installation:
            is_guest = False
            guest_installation = None

        attendence = Attendance(
            member_uid=member_uid,
            is_guest=is_guest,
            date=today,
            sunday_service=attendance_utils.is_sunday(),
            midweek_service=not attendance_utils.is_sunday(),
            guest_installation=guest_installation,
            global_gethsemane=attendance_utils.is_tuesday(),
        )

        return await member_db_handler.create_attendance_record(attendance=attendence)


async def get_todays_attendance(member_uid: UUID, date_: date):
    try:
        return await member_db_handler.get_todays_attendance(
            member_uid=member_uid, date_=date_
        )
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"member has not checked in for {date_}",
        )


async def get_attendance_via_uid(attendance_uid: UUID) -> AttendanceProfile:
    try:
        return await member_db_handler.get_member_attendance_record_via_uid(
            attendance_uid=attendance_uid
        )

    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="attendance record was not found",
        )


async def update_attendance_via_uid(
    attendance_uid: UUID, attendance_update: AttendanceUpdate
):
    try:
        attendance_profile = await get_attendance_via_uid(attendance_uid=attendance_uid)

        return await member_db_handler.update_member_attendance_record(
            member_uid=attendance_profile.member_uid,
            uid=attendance_uid,
            attendance_update=attendance_update,
        )

    except UpdateError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="attendance updated failed",
        )


async def delete_attendance_via_uid(attendance_uid: UUID):
    try:
        return await member_db_handler.delete_member_attendance_record(
            attendance_uid=attendance_uid
        )
    except DeleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="attendance record did not delete successfully",
        )


# GET MEMBERS and UD


async def get_members(installation: Installation, **kwargs):
    return await member_db_handler.get_installation_members(
        installation=installation, **kwargs
    )


async def get_member_via_member_uid(member_uid: UUID):
    try:
        return await member_db_handler.get_member(member_uid=member_uid)

    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"member with uid: {member_uid} not found",
        )
    ...


async def update_member(member_uid: UUID, member_update: MemberUpdate):
    await get_member_via_member_uid(member_uid=member_uid)
    try:
        await member_db_handler.update_member(
            member_uid=member_uid, member_update=member_update
        )
        return await get_member_via_member_uid(member_uid=member_uid)

    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error(
            f"update for member_uid: {member_uid}, with payload: {member_update.model_dump()}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"member with uid: {member_uid} failed to update",
        )
    ...


async def delete_member(member_uid: UUID):
    await get_member_via_member_uid(member_uid=member_uid)

    try:
        # trigger the job to Client Side
        await member_db_handler.delete_member(member_uid=member_uid)

        return {}
    except DeleteError as e:
        LOGGER.exception(e)
        LOGGER.error(f"delete for member: {member_uid} failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"member with uid: {member_uid} failed to delete",
        )


async def admin_dashboard_statistics(installation: Installation):
    member_uids = None
    if installation != Installation.global_:
        member_profiles = await get_members(installation=installation)

        member_uids = [member.member_uid for member in member_profiles.result_set]

    return await member_db_handler.member_attendance_statistics(
        installation=installation, member_uids=member_uids
    )
