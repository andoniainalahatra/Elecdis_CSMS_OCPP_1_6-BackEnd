from fastapi import APIRouter
from api.users.UserRoutes import router as user_routes
from api.auth.Auth_routes import router as auth_routes
from api.RFID.RFID_routes import router as rfid_routes
from api.CP.CP_routes import router as CP_routes
from api.Connector.Connector_routes import router as Connector_routes

routers = APIRouter()

routers.include_router(user_routes, prefix="/users", tags=["Users"])
routers.include_router(rfid_routes, prefix="/rfid", tags=["RFID"])
routers.include_router(auth_routes, prefix="/auth", tags=["Authentifications"])
routers.include_router(CP_routes, prefix="/cp", tags=["CP"])
routers.include_router(Connector_routes, prefix="/connector", tags=["Connector"])