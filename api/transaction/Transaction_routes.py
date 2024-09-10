from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.transaction.Transaction_service import *
from core.database import get_session
from models.Pagination import Pagination

router = APIRouter()


@router.get("/current/{page}/{limit}")
def get_current_session_list(session : Session = Depends(get_session),page:int=1, limit:int=10):
    return get_current_sessions(session, Pagination(page=page, limit=limit))

@router.get("/current/count")
def count_current_sessions(session : Session = Depends(get_session)):
    return {"count_current_session":count_current_session(session)}

@router.get("/total")
def total_session_charge(session: Session = Depends(get_session)):
    return {"total_sessions":total_session_de_charges(session)}

@router.get("/all/{page}/{limit}")
def get_all_sessions(session: Session = Depends(get_session), page:int=1, limit:int=10):
    return get_all_session(session, Pagination(page=page, limit=limit))