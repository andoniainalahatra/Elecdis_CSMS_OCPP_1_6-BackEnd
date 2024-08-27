from fastapi import APIRouter

from api.users.UserMethods import get_all_users

router = APIRouter()

@router.get("/client")
def get_list_client():
    return {"client": "client"}

@router.get("/")
def get_all():
    return get_all_users()