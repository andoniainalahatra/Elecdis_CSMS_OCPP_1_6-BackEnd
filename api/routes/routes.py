from fastapi import APIRouter
from api.users.UserRoutes import router as user_routes
from api.auth.Auth_routes import router as auth_routes
from api.RFID.RFID_routes import router as rfid_routes
from api.CP.CP_routes import router as CP_routes
from api.Connector.Connector_routes import router as Connector_routes
from api.transaction.Transaction_routes import router as transaction_routes
from api.subscription.Subscription_routes import router as subscription_routes
from api.userGroup.userGroup_routes import router as userGroup_routes
from api.tarifs.Tarifs_routes import router as tarifs_routes
routers = APIRouter()

routers.include_router(user_routes, prefix="/users", tags=["Users"])
routers.include_router(rfid_routes, prefix="/rfid", tags=["RFID"])
routers.include_router(auth_routes, prefix="/auth", tags=["Authentifications"])
routers.include_router(CP_routes, prefix="/cp", tags=["CP"])
routers.include_router(Connector_routes, prefix="/connector", tags=["Connector"])
routers.include_router(transaction_routes, prefix="/transaction", tags=["Transaction"])
routers.include_router(subscription_routes, prefix="/subscription", tags=["subscriptions"])
routers.include_router(userGroup_routes, prefix="/user_group", tags=["user_group"])
routers.include_router(tarifs_routes, prefix="/tarifs", tags=["tarifs"])
