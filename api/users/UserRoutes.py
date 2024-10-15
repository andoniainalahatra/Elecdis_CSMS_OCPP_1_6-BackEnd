import asyncio

from fastapi import APIRouter, HTTPException, status, Depends, File

from api.users.UserServices import *
from api.auth.Auth_services import oauth_2_scheme, get_current_user
from api.auth.RoleChecker import RoleChecker
from api.auth.Auth_services import update_user
from typing import Annotated

router = APIRouter()
@router.get("/search")
def search_user(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        search: str, session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):

    return search_queries_users(search, session, page, number_items)
@router.get("/client")
def get_list_client(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        session: Session=Depends(get_session),
        page: Optional[int] = 1,
        number_items: Optional[int] = 50
):
    return get_all_clients(session=session,page=page, number_items=number_items)

@router.get("/")
def get_all(
        token: str = Depends(oauth_2_scheme),
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        session: Session=Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_users(session=session, page=page, number_items=number_items)

@router.get("/Admin")
def get_admin(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],

        session: Session=Depends(get_session),
        page: Optional[int] = 1,
        number_items: Optional[int] = 50
):
    return get_all_Admins(session=session,page=page, item_numbers=number_items)

@router.get("/current")
async def get_current_user_api(token: str = Depends(oauth_2_scheme), session: Session=Depends(get_session)):
    return  await (get_current_user(session, token))

# @router.get("/current/sessions")
# async def get_All_current_user_sessions(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
#     return get_user_sessions_list(user=await get_current_user(session, token), session=session, page=page, number_items=number_items)


# @router.get("/current/transactions")
# async def get_All_current_user_transactions(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
#     return get_user_transactions_list(user=await get_current_user(session, token), session=session , page=page, number_items=number_items)

# @router.get("/transactions/{user_id}")
# async def get_all_user_sessions_by_user_id(user_id: int, session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
#     return get_user_sessions_list(user=get_user_by_id(user_id, session), session=session, page=page, number_items=number_items)


@router.get("/current/tags")
def get_all_current_user_tags(token: str = Depends(oauth_2_scheme), session: Session = Depends(get_session), user: UserData = Depends(get_current_user), page:Optional[int]=1, number_items:Optional[int]=50):
    tags = get_user_tags_list(user=user, session=session, page=page, number_items=number_items)
    return tags

@router.get("/tags/{user_id}")
async def get_all_user_tags_by_user_id(user_id: int, session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    tags = get_user_tags_list(user=await get_user_by_id(user_id, session), session=session, page=page, number_items=number_items)
    return tags
@router.get("/current/profile")
def get_current_user_profile(
        token: str = Depends(oauth_2_scheme),
        session: Session = Depends(get_session) , user: UserData = Depends(get_current_user)):
    transactions = get_user_transactions_list(user, session)
    sessions = get_user_sessions_list(user, session)
    return {"user": user, "transactions": transactions, "sessions": sessions}

@router.get("/profile/{user_id}")
def get_user_profile_by_id(user_id: int, session: Session = Depends(get_session)):
    user = get_user_by_id(user_id, session)
    return {"user": get_user_data(user)}

@router.put("/profile/{id}")
def update_user_profile(user_to_update:UserUpdate,id:int,
                        # token: str = Depends(oauth_2_scheme),
                        session: Session = Depends(get_session)):
    try :
        update_user(user_to_update, session,id)
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "User updated successfully"}

# @router.post
@router.get("/{id}")
def get_user_by_id_route(id: int, session: Session = Depends(get_session)):
        user = get_user_by_id(id, session)
        if user is None:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="User not found")
        return set_update_user_data(user)
@router.delete("/{id}")
def delete_user_by_id(id: int, session: Session = Depends(get_session)):
    try:
        delete_user(id, session)
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "User deleted successfully"}
@router.get("/new_clients/")
def get_new_clients(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        month: Optional[int]=None, year: Optional[int]=None, session: Session = Depends(get_session)):
    clients = get_new_clients_lists(session=session,mois=month, annee=year)
    if year is None:
        year = datetime.utcnow().year
    return {"clients ":clients,
            "month": month,
            "year": year}

@router.get("/new_clients/count")
def count_all_new_clients_based_on_month_and_years(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        month: Optional[int]=None, year: Optional[int]=None, session: Session = Depends(get_session)):
    if year is None:
        year = datetime.utcnow().year
    return {"count ":count_new_clients(mois=month, annee=year, session=session),
            "month": month,
            "year": year}

@router.post("/import_users_from_csv")
async def import_users_from_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    message = await upload_user_from_csv(file, session)
    if message.get("logs"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(message["logs"]))
    else:
        print(message)
    return {"message": "Users imported successfully"}

