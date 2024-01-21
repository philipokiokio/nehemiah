from enum import Enum
from typing import Optional
from fastapi import status


def payload_builder(status: int, detail: str, header: Optional[dict] = None):
    payload = {"status_code": status, "detail": detail}
    if header:
        payload["header"] = header
    return payload


class ErrorEnum(Enum):
    invite_token = payload_builder(
        status=status.HTTP_404_NOT_FOUND, detail="Invalid invitation code"
    )

    incorrect_credential = payload_builder(
        status=status.HTTP_401_UNAUTHORIZED,
        detail="invalid email or password credential",
    )

    redis_not_found = payload_builder(
        status=status.HTTP_400_BAD_REQUEST, detail="token expired or not valid"
    )

    # AGENT ERRORS
    admin_not_found = payload_builder(
        status=status.HTTP_404_NOT_FOUND, detail="admin agent not found"
    )
    member_create_error = payload_builder(
        status=status.HTTP_400_BAD_REQUEST, detail="agent not created"
    )
    member_found = payload_builder(
        status=status.HTTP_400_BAD_REQUEST, detail="this member exists "
    )
    member_not_found = payload_builder(
        status=status.HTTP_404_NOT_FOUND, detail="member not found"
    )

    def __call__(self):
        return self.value
