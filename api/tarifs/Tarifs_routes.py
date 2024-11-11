from fastapi import APIRouter, Depends
from datetime import datetime

from api.tarifs.Tarifs_models import Tariff_create
from core.database import get_session
from api.tarifs.Tarifs_services import *

router = APIRouter()

@router.get("/by_end_of_transaction")
def get_tarifs_by_end_of_transaction(end_transaction_date:datetime, session :Session= Depends(get_session)):
    return get_one_tarif_from_trans_end(end_trans=end_transaction_date, session=session)
@router.post("/")
def create_tarif(create_data:Tariff_create, session :Session= Depends(get_session)):
    return create_tariff(create_data, session)
@router.get("/")
def get_all_tarifs(session :Session= Depends(get_session),page:int=1, number_items:int=50):
    return get_all_tariff(session, page, number_items)

@router.delete("/{id}")
def delete_tarif(id:int, session :Session= Depends(get_session)):
    return delete_tariff(id, session)


@router.put("/{id}")
def update_tarif(id:int, create_data:Tariff_update, session :Session= Depends(get_session)):
    return update_tariff(id, create_data, session)