from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from checkin.routers.admin_route import api_router as admin_router
from checkin.routers.member_route import api_router as member_router


def intialize() -> FastAPI:
    app = FastAPI()
    app.include_router(router=admin_router)
    app.include_router(router=member_router)

    return app


app = intialize()


@app.get("/", status_code=307)
def root():
    return RedirectResponse(url="/docs")
