from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.Historique_session.Historique_session_services import get_all_history, get_all_session_from_history, \
    get_all_HS_by_user
from core.database import get_session
from models.Pagination import Pagination

router = APIRouter()

@router.get("/")
def get_all_historique_session( session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_history(session, Pagination(page=page, limit=number_items))

@router.get("/session_list")
def get_all_sessions_from_history( id_historique_session:int,session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_session_from_history(id_history=id_historique_session,session_db=session, pagination=Pagination(page=page, limit=number_items))

@router.get("/users")
def get_all_history_by_id_user(id_user:int, session:Session=Depends(get_session),page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_HS_by_user(id_user,session,Pagination(page=page,limit=number_items))