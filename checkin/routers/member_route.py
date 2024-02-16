import checkin.services.member_service as member_service
from checkin.schemas.member_schemas import (
    Member,
    MemberProfile,
    MemberExtendedProfile,
    NewMember,
    Installation,
)
from fastapi import (
    APIRouter,
    status,
    Depends,
    Header,
)


api_router = APIRouter(prefix="/v1/members", tags=["Member Management"])


@api_router.post(
    path="/first-timer",
    status_code=status.HTTP_201_CREATED,
    response_model=MemberExtendedProfile,
)
async def add_first_timer(
    new_member: NewMember, installation: Installation = Installation
):
    return await member_service.create_first_time_member(
        new_member=new_member, installation=installation
    )


@api_router.post(
    path="/token/check-in",
    status_code=status.HTTP_200_OK,
    response_model=MemberExtendedProfile,
)
async def token_member_checkin(
    checkin_token: str = Header(), installation: Installation = Installation
):
    # depends on the Query

    return await member_service.member_checkin_via_checkin_token(
        checkin_token=checkin_token, installation=installation
    )


@api_router.post(
    path="/check-in",
    status_code=status.HTTP_200_OK,
    response_model=MemberExtendedProfile,
)
async def member_checkin(member: Member, installation: Installation = Installation):
    return await member_service.member_checkin(member=member, installation=installation)


# Update  Record
