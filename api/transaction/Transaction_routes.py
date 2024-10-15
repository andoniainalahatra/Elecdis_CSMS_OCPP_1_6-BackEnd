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


@router.get("/rfid/{rfid}")
def get_charging_session_by_rfid(rfid: str, session_db: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_transactions_by_user_tags(user_tag=rfid, session=session_db, page=page, number_items=number_items)
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

@router.get("/average_duration")
def get_average_duration_of_sessions(session: Session = Depends(get_session)):
    return moyenne_session_duration(session)

@router.get("/heures_de_pointes")
def get_heures_de_pointes_des_sessions(session: Session = Depends(get_session)):
    return get_heures_de_pointes(session)

@router.get("/graphes_sessions")
def get_graphes_sessions(session: Session = Depends(get_session), date_selected:Optional[date]=datetime.now().date()):
    return get_session_data_chart(session,date_selected)
@router.get("/{user_id}")
def get_charging_session_by_user_Id(user_id: int, session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    return get_transactions_by_user_id(user_id=user_id, session=session, page=page, number_items=number_items)
