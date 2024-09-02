import asyncio

from fastapi import APIRouter, HTTPException, status, Depends

from api.users.UserServices import *
from api.auth.Auth_services import oauth_2_scheme, get_current_user
from api.auth.RoleChecker import RoleChecker
from api.auth.Auth_services import update_user
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

@router.get("/sessions")
async def get_user_sessions(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session)):
    return get_user_sessions_list(await get_current_user(session, token), session)


@router.get("/transactions")
async def get_user_transactions(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session)):
    return get_user_transactions_list(await get_current_user(session, token), session)


@router.get("/tags")
def get_user_tags(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session), user: UserData = Depends(get_current_user)):
    tags = get_user_tags_list(user, session)
    return tags

@router.get("/profile")
def get_user_profile(
        token: str = Depends(oauth_2_scheme),
        session: Session = Depends(get_session) , user: UserData = Depends(get_current_user)):
    transactions = get_user_transactions_list(user, session)
    sessions = get_user_sessions_list(user, session)
    return {"user": user, "transactions": transactions, "sessions": sessions}

@router.put("/profile")
def update_user_profile(user_to_update: UserUpdate, token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session)):
    try :
        update_user(user_to_update, session)
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "User updated successfully"}

# @router.post