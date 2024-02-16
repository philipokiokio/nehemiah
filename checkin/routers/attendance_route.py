import checkin.services.member_service as attendance_service
from fastapi import APIRouter, status, Depends, Header
from checkin.schemas.member_schemas import (
    Member,
    MemberUpdate,
    MemberExtendedProfile,
    AttendanceUpdate,
    PaginatedMemberProfile,
    AttendanceProfile,
    Installation,
    NewMember,
)
from checkin.schemas.auth_schemas import AdminUserProfile
from checkin.services.service_utils.auth_utils import get_current_user
from uuid import UUID

api_router = APIRouter(prefix="/v1/attendance", tags=["Attendance Management"])


@api_router.post(
    path="/check-in",
    status_code=status.HTTP_200_OK,
    response_model=MemberExtendedProfile,
)
async def admin_member_checkin(
    member: Member,
    installation: Installation = Header(Installation),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):

    return await attendance_service.member_checkin(
        member=member, installation=installation
    )


@api_router.post(
    "/new-member",
    status_code=status.HTTP_201_CREATED,
    response_model=MemberExtendedProfile,
)
async def admin_new_member_checkin(
    new_member: NewMember,
    installation: Installation = Header(Installation),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await attendance_service.create_first_time_member(
        new_member=new_member, installation=installation
    )


@api_router.get(
    "s/", status_code=status.HTTP_200_OK, response_model=PaginatedMemberProfile
)
async def get_members(
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await attendance_service.get_members(installation=admin_profile.installation)


@api_router.get(
    "/{member_uid}",
    status_code=status.HTTP_200_OK,
    response_model=MemberExtendedProfile,
)
async def get_member(
    member_uid: UUID,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await attendance_service.get_member_via_member_uid(member_uid=member_uid)


@api_router.patch(
    "/{member_uid}",
    status_code=status.HTTP_200_OK,
    response_model=MemberExtendedProfile,
)
async def update_member(
    member_uid: UUID,
    member_update: MemberUpdate,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await attendance_service.update_member(
        member_uid=member_uid, member_update=member_update
    )


@api_router.delete(
    "/{member_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_member(
    member_uid: UUID,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):

    return await attendance_service.delete_member(member_uid=member_uid)


@api_router.get("s/dashboard", status_code=status.HTTP_200_OK)
async def get_member_dashboard(
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await attendance_service.admin_dashboard_statistics(
        installation=admin_profile.installation
    )


@api_router.patch(
    "s/{uid}", status_code=status.HTTP_200_OK, response_model=AttendanceProfile
)
async def update_attendance_profile(
    uid: UUID,
    attendance_update: AttendanceUpdate,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):

    return await attendance_service.update_attendance_via_uid(
        attendance_uid=uid, attendance_update=attendance_update
    )
