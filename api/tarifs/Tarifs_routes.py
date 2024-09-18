from fastapi import APIRouter, Depends
from datetime import datetime
from core.database import get_session
from api.tarifs.Tarifs_services import *

router = APIRouter()

@router.get("/by_end_of_transaction")
def get_tarifs_by_end_of_transaction(end_transaction_date:datetime, session :Session= Depends(get_session)):
    return get_one_tarif_from_trans_end(end_trans=end_transaction_date, session=session)