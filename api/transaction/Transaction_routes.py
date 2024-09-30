from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.transaction.Transaction_service import *
from api.users.UserServices import get_user_transactions_list, get_user_by_id
from core.database import get_session
from models.Pagination import Pagination

router = APIRouter()

@router.get("/details/{session_id}")
async def get_transaction_details_by_session_id(session_id: int, session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_transactions_details_by_session(session, session_id, page=page, number_items=number_items)
@router.get("/current/")
def get_current_session_list(session : Session = Depends(get_session),page:Optional[int]=1, number_items:Optional[int]=10):
    return get_current_sessions(session, Pagination(page=page, limit=number_items))
@router.get("/done/")
def get_done_session_list(session : Session = Depends(get_session),page:Optional[int]=1, number_items:Optional[int]=10):
    return get_done_sessions(session, Pagination(page=page, limit=number_items))

@router.get("/current/count")
def count_current_sessions(session : Session = Depends(get_session)):
    return {"count_current_session":count_current_session(session)}

@router.get("/total")
def total_session_charge(session: Session = Depends(get_session)):
    return {"total_sessions":total_session_de_charges(session)}

@router.get("/all/")
def get_all_sessions(session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=10):
    return get_all_session(session, Pagination(page=page, limit=number_items))

@router.get("/test")
def test(session: Session = Depends(get_session)):
    ses= get_session_by_id(session, 1)
    s=get_sums_transactions(session, 2)
    print(s)
    return s