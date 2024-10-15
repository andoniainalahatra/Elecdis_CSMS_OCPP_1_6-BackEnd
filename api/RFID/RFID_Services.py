from datetime import datetime
from typing import List
from sqlmodel import cast, Integer

from fastapi import UploadFile, HTTPException
from api.RFID.RFID_models import *
from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import Tag, User, StatusEnum, Rfid_usage_history
from sqlmodel import Session, select, func
from core.utils import *
from api.users.UserServices import get_user_from_email, get_user_by_id
from api.auth.Auth_services import get_password_hash, verify_email_structure


def create_rfid_service(rfid: Rfid_create, session: Session, can_commit: bool = True):
    try:
        # check user
        user = session.exec(select(User).where(User.id == rfid.user_id)).first()
        if user == None:
            raise Exception(f"User with id {rfid.user_id} does not exist.")
        # check rfid
        rfid.rfid = rfid.rfid.strip()
        # check if rfid is already asigned to an user
        tag=get_by_tag(session=session, tag=rfid.rfid)
        if tag is not None and tag.user_id == rfid.user_id:
            raise Exception(f"RFID tag {rfid.rfid} already exists.")
        if rfid.rfid is None or rfid.rfid == "":
            raise ValueError(f"The field 'tag' cannot be empty.")
        tag = Tag(tag=rfid.rfid, user_id=rfid.user_id, status= StatusEnum.active)

        session.add(tag)
        if can_commit:
            session.commit()
        session.refresh(tag)
        return tag
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


def update_rfid_service(rfid: Rfid_update, session: Session, id:int):
        print("1")
        tag: Tag = session.exec(select(Tag).where(Tag.id == id, cast(Tag.state, Integer) !=DELETED_STATE)).first()
        if tag is None:
            print("2")
            raise Exception(f"Tag with id {id} does not exist.")

        if rfid.rfid is not None:
            print("3")
            # check rfid
            rfid.rfid = rfid.rfid.strip()
            if rfid.rfid is None or rfid.rfid == "":
                raise ValueError(f"The field 'tag' cannot be empty.")

            tag.tag = rfid.rfid
        if rfid.user_id is not None:
            user = get_user_by_id(rfid.user_id, session)
            if user == None:
                raise Exception(f"User with id {rfid.user_id} does not exist.")
            tag.user_id = rfid.user_id
        tag.updated_at = datetime.now()
        session.add(tag)
        session.commit()
        session.refresh(tag)
        return tag



def delete_rfid_service(id: int, session: Session):
    try:
        tag: Tag = session.exec(select(Tag).where(Tag.id == id, cast(Tag.state, Integer) !=DELETED_STATE)).first()
        if tag is None:
            raise Exception(f"Tag with id {id} does not exist.")
        tag.state= DELETED_STATE
        tag.updated_at = datetime.now()
        session.add(tag)
        session.commit()
        return {"message": "Tag deleted successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

def get_all_rfid(session: Session, page: int = 1, number_items: int = 50):
    pagination = Pagination(page=page, limit=number_items)
    total_items = session.exec(select(func.count(Tag.id)).where(cast(Tag.state, Integer) != DELETED_STATE)).one()
    pagination.total_items = total_items
    return {"data":get_rfid_data_lists(session.exec(select(Tag).where(cast(Tag.state, Integer) != DELETED_STATE)).all(), session), "pagination": pagination.dict()}

def get_deleted_rfid(session: Session, page: int = 1, number_items: int = 50):
    pagination = Pagination(page=page, limit=number_items)
    total_items = session.exec(select(func.count(Tag.id)).where(cast(Tag.state, Integer) == DELETED_STATE)).one()
    pagination.total_items = total_items
    return {"data":get_rfid_data_lists(session.exec(select(Tag).where(cast(Tag.state, Integer) == DELETED_STATE)).all(), session), "pagination": pagination.dict()}

def get_rfid_data(data : Tag, session: Session):
    if data is None:
        return None
    # get last used
    history= (get_rfid_use_history(session, data.id))
    hist =[Historique_rfids( date= data.created_at, action = data.action, session_id=data.session_id) for data in history]
    return Rfid_data(
        id=data.id,
        rfid=data.tag,
        user_id=data.user_id,
        user_name=f"{data.user.first_name} {data.user.last_name}",
        status=data.status,
        last_used=get_last_used_date_rfid(session, data.id),
        registration=data.created_at,
        history=hist
    )

def get_rfid_data_lists(datas: List[Tag], session: Session):
    return [get_rfid_data(data, session) for data in datas]

async def upload_rfid_from_csv(file: UploadFile, session: Session, create_non_existing_users: bool = True):
    logs = []
    try:
        # Start a transaction
        with session.begin():
            # 1 - Read the file
            datas = await get_datas_from_csv(file)
            line = 1
            for data in datas:
                # check email structure
                try:
                    verify_email_structure(data["email"])
                except Exception as e:
                    logs.append({"message": f" email {data['email']} is in a wrong format.", "line": line})
                    line += 1
                    continue
                # check if the rfid already exists
                tag = session.exec(select(Tag).where(Tag.tag == data["rfid"], cast(Tag.state, Integer) !=DELETED_STATE)).first()
                if tag is not None:
                    logs.append({"message": f"RFID tag {data['rfid']} already exists.", "line": line})
                    line += 1
                    continue

                #  check if the user exists
                user = get_user_from_email(data["email"], session)
                if user is None:
                    if create_non_existing_users:
                        # create the user
                        user = User(first_name=data["first_name"], last_name=data["last_name"], email=data["email"],
                                    password=get_password_hash(DEFAULT_USER_PASSWORD))
                        session.add(user)
                        session.flush()
                    else:
                        logs.append({"message": f"User with email {data['email']} does not exist.", "line": line})
                        line += 1
                        continue
                # create the rfid
                create_rfid_service(Rfid_create(rfid=data["rfid"], user_id=user.id), session, can_commit=False)
                line += 1

            if len(logs) > 0:
                # Rollback the transaction if there are logs
                session.rollback()
                return {"message": "RFID tags imported with errors", "logs": logs}

            # Commit the transaction if no logs
            session.commit()
            return {"message": "RFID tags imported successfully"}
    except Exception as e:
        session.rollback()
        return {"message": f"Error: {str(e)}"}
def get_by_tag(session: Session, tag: str):
    return session.exec(select(Tag).where(Tag.tag == tag, Tag.state!=DELETED_STATE )).first()
def get_rdif_by_id(session: Session, id: int):

    datas =get_rfid_data(session.exec(select(Tag).where(Tag.id == id, Tag.state!=DELETED_STATE )).first(), session)
    if datas is None:
        raise HTTPException(status_code=404, detail="RFID not found")
    return datas
def get_user_by_tag(session : Session, tag : str):
    tag = session.exec(select(Tag).where(Tag.tag == tag )).first()
    if tag is None:
        return None
    return tag.user

# todo : add history to rfid / status / get details rfid

def get_last_used_date_rfid(session: Session, id_tag: int):
    date_last_used = session.exec(select(func.max(Rfid_usage_history.created_at)).where(Rfid_usage_history.tag_id == id_tag)).first()
    return date_last_used

def get_rfid_use_history(session: Session, id_tag: int):
    return session.exec(select(Rfid_usage_history).where(Rfid_usage_history.tag_id == id_tag)).all()

