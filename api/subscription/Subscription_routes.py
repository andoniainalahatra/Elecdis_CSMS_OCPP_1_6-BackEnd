from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends

from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import Subscription
from sqlmodel import Session, select, func
from api.subscription.Subscription_models import *

router = APIRouter()

@router.post("/subscriptions/", response_model=Subscription)
def create_subscription(

        subscription: Subscription, session: Session = Depends(get_session)):
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription

# READ ALL (GET)
@router.get("/subscriptions/")
def read_subscriptions(session: Session = Depends(get_session), page:Optional[int]=1, number_items:Optional[int]=50):
    pagination = Pagination(page=page, limit=number_items)
    subscriptions = session.exec(select(Subscription).offset(pagination.offset).limit(pagination.limit)).all()
    count = session.exec(select(func.count(Subscription.id))).one()
    pagination.total_items = count
    return {"data":subscriptions, "pagination":pagination.dict()}

# READ ONE (GET)
@router.get("/subscriptions/{subscription_id}", response_model=Subscription)
def read_subscription(subscription_id: int, session: Session = Depends(get_session)):
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

# UPDATE (PUT)
@router.put("/subscriptions/{subscription_id}", response_model=Subscription)
def update_subscription(subscription_id: int, subscription_data: Subscription, session: Session = Depends(get_session)):
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription.type_subscription = subscription_data.type_subscription
    session.commit()
    session.refresh(subscription)
    return subscription

# DELETE (DELETE)
@router.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, session: Session = Depends(get_session)):
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    session.delete(subscription)
    session.commit()
    return {"ok": True}