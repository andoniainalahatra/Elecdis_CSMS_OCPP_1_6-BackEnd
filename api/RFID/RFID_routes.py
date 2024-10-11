import csv
import io

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

import api
from api.RFID.RFID_models import Rfid_update, Rfid_create
from core.database import get_session
from core.utils import get_datas_from_csv
from api.RFID.RFID_Services import update_rfid_service, delete_rfid_service, upload_rfid_from_csv, create_rfid_service, \
    get_all_rfid, get_deleted_rfid, get_rdif_by_id
from models.elecdis_model import StatusEnum

router = APIRouter()


@router.put("/{id}")
def update_rfid(
                # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
                id:int,
                update_data: Rfid_update, session: Session = Depends(get_session)):
    try:
        update_rfid_service(update_data, session, id)
    except Exception as e:
        print("errors : ",e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "RFID updated successfully"}


@router.post("/")
def create_rfid(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],

        create_data: Rfid_create, session: Session = Depends(get_session)):
    create_rfid_service(rfid=create_data, session=session)
    return {"message": "RFID creaed successfully"}



@router.delete("/{id}")
def delete_rfid(        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        id: int, session: Session = Depends(get_session)):
    return delete_rfid_service(id, session)


@router.post("/import_from_csv")
async def import_from_csv(file: UploadFile = File(...), session : Session = Depends(get_session)):
    message = await upload_rfid_from_csv(file, session, create_non_existing_users=True)
    if message.get("logs"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(message["logs"]))
    return {"message": "RFID imported successfully"}

@router.get("/all")
def get_all_rfid_list(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        session: Session = Depends(get_session), page: int = 1, number_items: int = 50):
    return get_all_rfid(session, page, number_items)

@router.get("/deleted")
def get_deleted_rfid_list(
        # _: Annotated[bool, Depends(RoleChecker(allowed_roles=["Admin"]))],
        session: Session = Depends(get_session)):

    return get_deleted_rfid(session)

@router.get("/{id}")
def get_rfid_by_id_routes(id: int, session: Session = Depends(get_session)):
    rfid = get_rdif_by_id(id=id, session=session)
    if rfid is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFID not found")
    return rfid

@router.put("/activate/{id}")
def activate_rfid_routes(id: int, session: Session = Depends(get_session)):
    rfid = get_rdif_by_id(id=id, session=session)
    if rfid is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFID not found")
    if rfid.status != StatusEnum.active:
        rfid.status = StatusEnum.active
        session.add(rfid)
        session.commit()
    return rfid

@router.put("/deactivate/{id}")
def deactivate_rfid_routes(id: int, session: Session = Depends(get_session)):
    rfid = get_rdif_by_id(id=id, session=session)
    if rfid is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFID not found")
    if rfid.status != StatusEnum.inactive:
        rfid.status = StatusEnum.inactive
        session.add(rfid)
        session.commit()
    return rfid
