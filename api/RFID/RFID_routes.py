import csv
import io

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from api.RFID.RFID_models import Rfid_update, Rfid_create
from core.database import get_session
from core.utils import get_datas_from_csv
from api.RFID.RFID_Services import create_rfid, update_rfid, delete_rfid, upload_rfid_from_csv
router = APIRouter()


@router.put("/")
def update_rfid(update_data: Rfid_update, session: Session = Depends(get_session)):
    update_rfid(update_data, session)


@router.post("/")
def create_rfid(create_data: Rfid_create, session: Session = Depends(get_session)):
    create_rfid(create_data, session)


@router.delete("/{id}")
def delete_rfid(id: int, session: Session = Depends(get_session)):
    delete_rfid(id, session)


@router.post("/import_from_csv")
async def import_from_csv(file: UploadFile = File(...), session : Session = Depends(get_session)):
    message = await upload_rfid_from_csv(file, session, create_non_existing_users=True)
    if message.get("logs"):
        print(message["logs"])
    else :
        print(message)
    return {}
