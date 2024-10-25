from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.userCredit.UserCredit_services import add_user_credit, get_user_credit_solde_by_idTag, debiter_user_credit, \
    historique_credit
from core.database import get_session

router = APIRouter()

@router.post("/add_credit")
def add_credit_to_user_account(id_rfid:int, credit:float, session: Session = Depends(get_session)):
    add_user_credit(session=session, amount = credit, idtag=id_rfid)
    return get_user_credit_solde_by_idTag(session=session, idtag=id_rfid)
@router.get("/solde")
def get_solde(id_rfid:int, session: Session = Depends(get_session)):
    return get_user_credit_solde_by_idTag(session=session, idtag=id_rfid)

@router.post("/debit_credit")
def debit_credit_to_user_account(id_rfid:int, credit:float, session: Session = Depends(get_session)):
    debiter_user_credit(session=session, amount = credit, idtag=id_rfid)
    return get_user_credit_solde_by_idTag(session=session, idtag=id_rfid)

@router.get("/historique_credit")
def get_credit_history(id_rfid:int, session: Session = Depends(get_session)):
    return historique_credit(session=session, idtag=id_rfid)