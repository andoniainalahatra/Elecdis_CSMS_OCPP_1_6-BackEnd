from fastapi import APIRouter
from api.users.UserRoutes import router as user_routes
from api.auth.UserAuthentification import router as auth_routes
from api.RFID.RFID_routes import router as rfid_routes

routers = APIRouter()

routers.include_router(user_routes, prefix="/users", tags=["Users"])
routers.include_router(rfid_routes, prefix="/rfid", tags=["RFID"])
routers.include_router(auth_routes, prefix="/auth", tags=["Authentifications"])