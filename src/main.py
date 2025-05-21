from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.swagger import custom_openapi
from src.auth.routers import router as auth_router
from src.user.routers import (
    router as user_router,
    admin_router as admin_user_router,
)
from src.organization.routers import router as organization_router
from src.video.routers import router as video_router, admin_router as admin_video_router
from src.core.exceptions import AppBaseException

app = FastAPI()

all_routers = [
    auth_router,
    organization_router,
    user_router,
    video_router,
    admin_user_router,
    admin_video_router,
]
for router in all_routers:
    app.include_router(router)

app.openapi = lambda: custom_openapi(app)


@app.exception_handler(AppBaseException)
async def handle_custom_exceptions(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.get("/")
async def health_check():
    return {"status": "ok"}
