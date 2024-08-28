import asyncio

from fastapi import APIRouter

from api.users.UserServices import *
from api.auth.UserAuthentification import oauth_2_scheme, get_current_user, RoleChecker
from typing import Annotated

router = APIRouter()

@router.get("/client")
def get_list_client(_: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))]):
    return get_all_clients(next(get_session()))

@router.get("/")
def get_all(token: str = Depends(oauth_2_scheme), session: Session=Depends(get_session)):
    return get_all_users(next(get_session()))

@router.get("/Admin")
def get_admin():
    return get_all_Admins(next(get_session()))

@router.get("/current")
async def get_current_user_api(token: str = Depends(oauth_2_scheme), session: Session=Depends(get_session)):
    return get_user_data( await (get_current_user(session, token)))