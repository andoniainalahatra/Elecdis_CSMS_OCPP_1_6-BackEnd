from datetime import datetime

from sqlalchemy.orm import Session as Session_db
from sqlmodel import select, func

from api.userCredit.UserCredit_models import Solde_data
from api.users.UserServices import *
from api.RFID.RFID_Services import *
from core.utils import *
from models.elecdis_model import UserCredit


def check_if_has_credit(session: Session_db, idtag: int):
    if get_user_credit_solde_by_idTag(session,idtag).solde<=MIN_SOLDE:
        return False
    return True


def get_user_credit_solde_by_idTag(session: Session_db, idtag: int,user_id:Optional[int]=None):
    solde = session.exec(select(func.coalesce(func.sum(UserCredit.credit_in)-func.sum(UserCredit.credit_out),0).label("solde"),UserCredit.credit_unit).where(UserCredit.id_tag == idtag).group_by(UserCredit.credit_unit)).first()
    if solde is None:
        return Solde_data(solde=0, user_id=0, unit=UNIT_KWH)
    userid= None
    if user_id is None:
        userid= get_rdif_by_id(session, idtag).user_id
    else:
        userid=user_id
    return Solde_data(solde=solde[0], user_id=userid, unit=solde[1])

def add_user_credit(session: Session_db, idtag: int, amount: float, reason="Recharge", can_commit: bool = True):
    uc= UserCredit(id_tag=idtag, credit_in=amount, reason = reason)
    session.add(uc)
    if can_commit:
        session.commit()
    return uc
def debiter_user_credit(session: Session_db, idtag: int, amount: float, can_commit: bool = True, reason=f"Debit pour une recharge le {datetime.now()}", session_id:Optional[int]=None):
    uc= UserCredit(id_tag=idtag, credit_out=amount, reason = reason)
    if session_id!=None:
        uc.reason+=f" numero de transaction : {session_id}"
    session.add(uc)
    print(f"{amount} debited from user {idtag}")
    if can_commit:
        session.commit()
    return uc

def historique_credit(session: Session_db, idtag: int):
    hi=session.exec(select(UserCredit).where(UserCredit.id_tag == idtag)).all()
    result=[]
    from api.RFID.RFID_Services import get_rdif_by_id

    for i in hi:
        solde=0
        tag= get_rdif_by_id(session=session, id=idtag)
        if i.credit_in!=0:
            solde=i.credit_in
        elif i.credit_out!=0:
            solde=-i.credit_out
        res={
            "amount": solde,
            "unit": i.credit_unit,
            "date": i.created_at,
            "reason": i.reason,
            "rfid": tag.rfid,
            "user": tag.user_name
        }
        result.append(res)
    return result
def get_sum_energy_consumed_in_a_session_with_applied_tarifs(session_id:int, session_db:Session_db):
    sum_transactions = session_db.exec(select(func.sum(Transaction.consumed_energy_added)).where(Transaction.session_id == session_id)).first()
    return sum_transactions
def debit_credit_to_user_account_after_session(session: Session_db, idtag: int, session_id: int):
    todebit=get_sum_energy_consumed_in_a_session_with_applied_tarifs( session_id,session)
    debiter_user_credit(session=session, amount=todebit, idtag=idtag, session_id=session_id)
    return get_user_credit_solde_by_idTag(session=session, idtag=idtag)

def check_if_sold_out(session: Session_db, idtag: int, value_to_add: float):
    if (get_user_credit_solde_by_idTag(session,idtag).solde-value_to_add)<=1:
        return True
    return False


