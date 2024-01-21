from pydantic import EmailStr
from checkin.schemas.auth_schemas import AdminUserProfile
import checkin.services.member_service as agent_service
from checkin.schemas.member_schemas import (
    Member,
    MemberProfile,
    Attendance,
    AttendanceProfile,
    AttendanceUpdate,
    MemberUpdate,
    PaginatedMemberProfile,
)
from fastapi import (
    APIRouter,
    Body,
    status,
    Depends,
    UploadFile,
)
from checkin.schemas.commons_schemas import PaginatedQuery
from checkin.services.service_utils.auth_utils import get_current_user
from checkin.schemas.auth_schemas import AdminUserProfile
from uuid import UUID


api_router = APIRouter(prefix="/v1/agents", tags=["Agent Management"])


@api_router.post(path="/invite", status_code=status.HTTP_201_CREATED)
async def invite_agent(
    email: EmailStr = Body(embed=True),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.create_admin_agent(
        admin_uid=admin_profile.admin_uid, email=email
    )


@api_router.get(
    path="/{agent_uid}", status_code=status.HTTP_200_OK, response_model=MemberProfile
)
async def get_agent(
    agent_uid: UUID, admin_profile: AdminUserProfile = Depends(get_current_user)
):
    return await agent_service.get_admin_agent(
        agent_uid=agent_uid, admin_uid=admin_profile.admin_uid
    )


@api_router.get(
    path="", status_code=status.HTTP_200_OK, response_model=PaginatedMemberProfile
)
async def get_agents(
    pagniated_query: PaginatedQuery = Depends(PaginatedQuery),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    # depends on the Query

    return await agent_service.get_admin_agents(
        admin_uid=admin_profile.admin_uid, **pagniated_query.model_dump()
    )


# DELETE RECORD
@api_router.delete(path="/{agent_uid}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_uid: UUID,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.delete_admin_agent(agent_uid=agent_uid)


# UPDATE RECORD
@api_router.patch(
    path="/{agent_uid}", status_code=status.HTTP_200_OK, response_model=AdminUserProfile
)
async def update_agent(
    agent_uid: UUID,
    agent_update: MemberUpdate,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.update_admin_agent(
        agent_uid=agent_uid, agent_update=agent_update
    )
