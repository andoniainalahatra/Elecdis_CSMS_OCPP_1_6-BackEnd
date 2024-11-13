from typing import List

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from api.tarifs.Tarifs_models import Tariff_create, TariffGroup_update, TariffGroup_create
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

@router.post("/tariff-groups/", response_model=TariffGroup)
def create_tariff_group_endpoint(create_data: TariffGroup_create, db: Session = Depends(get_session)):
    return create_tariff_group(create_data, db)

@router.put("/tariff-groups/{id}", response_model=TariffGroup)
def update_tariff_group_endpoint(id: int, update_data: TariffGroup_update, db: Session = Depends(get_session)):
    return update_tariff_group(id, update_data, db)

@router.delete("/tariff-groups/{id}")
def delete_tariff_group_endpoint(id: int, db: Session = Depends(get_session)):
    return delete_tariff_group(id, db)

@router.get("/tariff-groups/{id}", response_model=TariffGroup)
def get_tariff_group_by_id_endpoint(id: int, db: Session = Depends(get_session)):
    tariff_group = get_tariff_group_by_id(id, db)
    if not tariff_group:
        raise HTTPException(status_code=404, detail="Tariff group not found")
    return tariff_group

@router.get("/tariff-groups/")
def get_all_tariff_groups_endpoint(db: Session = Depends(get_session), page: int = 1, number_items: int = 50):
    return get_all_tariff_groups(db, page, number_items)