
from api.RFID.RFID_models import Rfid_create
from models.elecdis_model import Tag, User
from sqlmodel import Session, select


def create_rfid(rfid: Rfid_create, session : Session):
    try:
        # check user
        user = session.exec(select(User).where(User.id == rfid.user_id)).first()
        if user == None:
            raise Exception(f"User with id {rfid.user_id} does not exist.")
        # check rfid
        rfid.rfid= rfid.rfid.strip()
        if rfid.rfid is None or rfid.rfid == "":
            raise ValueError(f"The field 'tag' cannot be empty.")
        tag : Tag = Tag(tag=rfid.rfid, user_id=rfid.user_id)
        session.add(tag)
        session.commit()
        session.refresh(tag)
        return tag
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

def update_rfid(rfid: Rfid_create, session : Session):
    try:
        # check user
        user = session.exec(select(User).where(User.id == rfid.user_id)).first()
        if user == None:
            raise Exception(f"User with id {rfid.user_id} does not exist.")
        # check rfid
        rfid.rfid= rfid.rfid.strip()
        if rfid.rfid is None or rfid.rfid == "":
            raise ValueError(f"The field 'tag' cannot be empty.")
        tag : Tag = session.exec(select(Tag).where(Tag.id == rfid.id)).first()
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
        tag : Tag = session.exec(select(Tag).where(Tag.id == id)).first()
        if tag is None:
            raise Exception(f"Tag with id {id} does not exist.")
        session.delete(tag)
        session.commit()
        return {"message": "Tag deleted successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}