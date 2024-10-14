from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from checkin.routers.admin_route import api_router as admin_router
from checkin.routers.member_route import api_router as member_router
from checkin.schemas.commons_schemas import Installation
from checkin.services.member_service import get_members
from checkin.routers.attendance_route import api_router as attendance_router


def intialize() -> FastAPI:
    app = FastAPI()
    app.include_router(router=admin_router)
    app.include_router(router=member_router)
    app.include_router(router=attendance_router)

    return app


app = intialize()


@app.get("/", status_code=307)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health-check", status_code=200)
async def health_check():
    await get_members(installation=Installation.akure.value)
    return {"keep_alive": True}
