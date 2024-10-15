from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status

from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import UserGroup
from sqlmodel import Session, select, func

router = APIRouter()
@router.post("/usergroups/", response_model=UserGroup)
def create_usergroup(usergroup: UserGroup, session: Session = Depends(get_session)):
    session.add(usergroup)
    session.commit()
    session.refresh(usergroup)
    return usergroup

# READ ALL avec pagination (GET)
@router.get("/usergroups/")
def read_usergroups(session: Session = Depends(get_session), page: Optional[int] = 1, number_items: Optional[int] = 50):
    pagination = Pagination(page=page, limit=number_items)

    # Récupérer les groupes avec la pagination
    usergroups = session.exec(select(UserGroup).offset(pagination.offset).limit(pagination.limit)).all()

    # Calculer le nombre total d'éléments
    count = session.exec(select(func.count(UserGroup.id))).one()
    pagination.total_items = count

    return {"data": usergroups, "pagination": pagination.dict()}

# READ ONE (GET)
@router.get("/usergroups/{usergroup_id}", response_model=UserGroup)
def read_usergroup(usergroup_id: int, session: Session = Depends(get_session)):
    usergroup = session.get(UserGroup, usergroup_id)
    if not usergroup:
        raise HTTPException(status_code=404, detail="UserGroup not found")
    return usergroup

# UPDATE (PUT)
@router.put("/usergroups/{usergroup_id}", response_model=UserGroup)
def update_usergroup(usergroup_id: int, usergroup_data: UserGroup, session: Session = Depends(get_session)):
    usergroup = session.get(UserGroup, usergroup_id)
    if not usergroup:
        raise HTTPException(status_code=404, detail="UserGroup not found")

    usergroup.name = usergroup_data.name
    session.commit()
    session.refresh(usergroup)
    return usergroup

# DELETE (DELETE)
@router.delete("/usergroups/{usergroup_id}")
def delete_usergroup(usergroup_id: int, session: Session = Depends(get_session)):
    usergroup = session.get(UserGroup, usergroup_id)
    if not usergroup:
        raise HTTPException(status_code=404, detail="UserGroup not found")

    session.delete(usergroup)
    session.commit()
    return {"ok": True}
