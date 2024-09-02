from typing import List

from fastapi import UploadFile
from api.RFID.RFID_models import Rfid_create
from models.elecdis_model import Tag, User
from sqlmodel import Session, select
from core.utils import get_datas_from_csv, DEFAULT_USER_PASSWORD
from api.users.UserServices import get_user_from_email
from api.auth.UserAuthentification import get_password_hash, verify_email_structure


def create_rfid(rfid: Rfid_create, session: Session, can_commit : bool = True):
    try:
        # check user
        user = session.exec(select(User).where(User.id == rfid.user_id)).first()
        if user == None:
            raise Exception(f"User with id {rfid.user_id} does not exist.")
        # check rfid
        rfid.rfid = rfid.rfid.strip()
        if rfid.rfid is None or rfid.rfid == "":
            raise ValueError(f"The field 'tag' cannot be empty.")
        tag: Tag = Tag(tag=rfid.rfid, user_id=rfid.user_id)
        session.add(tag)
        if can_commit:
            session.commit()
        session.refresh(tag)
        return tag
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


def update_rfid(rfid: Rfid_create, session: Session):
    try:
        # check user
        user = session.exec(select(User).where(User.id == rfid.user_id)).first()
        if user == None:
            raise Exception(f"User with id {rfid.user_id} does not exist.")
        # check rfid
        rfid.rfid = rfid.rfid.strip()
        if rfid.rfid is None or rfid.rfid == "":
            raise ValueError(f"The field 'tag' cannot be empty.")
        tag: Tag = session.exec(select(Tag).where(Tag.id == rfid.id)).first()
        if tag is None:
            raise Exception(f"Tag with id {rfid.id} does not exist.")
        tag.tag = rfid.rfid
        tag.user_id = rfid.user_id
        session.commit()
        session.refresh(tag)
        return tag
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


def delete_rfid(id: int, session: Session):
    try:
        tag: Tag = session.exec(select(Tag).where(Tag.id == id)).first()
        if tag is None:
            raise Exception(f"Tag with id {id} does not exist.")
        session.delete(tag)
        session.commit()
        return {"message": "Tag deleted successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


async def upload_rfid_from_csv(file: UploadFile, session: Session, create_non_existing_users: bool = True):
    # 1.1 - check id the datas in the file are correct = check empty emails or incorrect email format
    # 2 - get the users in the datas and check if they exist if not create them
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
                tag = session.exec(select(Tag).where(Tag.tag == data["rfid"])).first()
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
                create_rfid(Rfid_create(rfid=data["rfid"], user_id=user.id), session, can_commit=False)
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
