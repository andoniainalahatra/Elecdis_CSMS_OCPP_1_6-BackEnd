from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.Historique_session.Historique_session_services import get_all_history
from core.database import get_session
from models.Pagination import Pagination

router = APIRouter()

@router.get("/")
def get_all_historique_session( session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_history(session, Pagination(page=page, limit=number_items))

@router.get("/")
def get_all_session_from_history( id_historique_session:int,session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_all_session_from_history(id_historique_session=id_historique_session,session=session, pagination=Pagination(page=page, limit=number_items))

