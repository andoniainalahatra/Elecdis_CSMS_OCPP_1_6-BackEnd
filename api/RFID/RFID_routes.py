from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.RFID.RFID_models import Rfid_update, Rfid_create
from core.database import get_session

router = APIRouter()


@router.put("/")
def update_rfid(update_data : Rfid_update, session : Session=Depends(get_session)):
    update_rfid(update_data, session)


@router.post("/")
def create_rfid(create_data : Rfid_create, session : Session=Depends(get_session)):
    create_rfid(create_data, session)

@router.delete("/{id}")
def delete_rfid(id : int , session : Session=Depends(get_session)):
    delete_rfid(id,session)