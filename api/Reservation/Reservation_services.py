from ocpp_scenario.ReserveNow import ReserveNow
from ocpp_scenario.CancelReservation import CancelReservation
import aio_pika
from aio_pika import Message as AioPikaMessage
from core.config import *
from core.utils import *
import json
from fastapi import HTTPException
from models.elecdis_model import Reservation,History_reservation,ChargePoint,Connector,Tag,User
from sqlmodel import Session
from api.Reservation.Resercation_models import reservation_create,create_history_reservation,data_history_reservation
from sqlmodel import Session, select,func,extract,case,desc,not_,join,and_
from datetime import date, datetime,timedelta
from core.config import TIME_ZONE
import pytz
from core.database import get_session

async def reserve_now(connectorId:int,idTag:str,reservationId:int,charge_point_id:str):
    reserve=ReserveNow()
    message = reserve.on_reserveNow(connectorId,idTag,reservationId)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )
        session : Session = next(get_session())
        timezone = pytz.timezone(TIME_ZONE)
        user=take_user_match_with_tag(tags=idTag,session=session)
        reserve=reservation_create(connector_id=f"{connectorId}{charge_point_id}",date_reservation=datetime.now(timezone),user_id=user.id,expirate_date=message[3]["expiryDate"])
        create_reservation(reserve,session)

        return {"status": "Message sent", "response": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
    
async def cancel_reservation(reservationId:int,charge_point_id:str):
    cancel=CancelReservation()
    message = cancel.on_cancelReservation(reservationId)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )
            
        session : Session = next(get_session())
        update_reservation_etat(reservation_id=reservationId,session=session)
        return {"status": "Message sent", "response": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")


def create_reservation(reserve:reservation_create, session : Session):
    try:
        reservation = session.exec(
            select(Reservation)
            .join(Connector, Reservation.connector_id == Connector.id)
            .where(
                and_(
                    reserve.date_reservation >= Reservation.date_reservation,
                    reserve.date_reservation <= Reservation.expirate_date,
                    Connector.id == reserve.connector_id,
                    Reservation.etat==1
                )
            )
        ).all()
        if reservation :
            raise HTTPException(status_code=500, detail=f"Occupée")
        expiry_date =(reserve.date_reservation+ timedelta(hours=2))
        charge : Reservation = Reservation(connector_id=reserve.connector_id,date_reservation=reserve.date_reservation,user_id=reserve.user_id,expirate_date=expiry_date,etat=1)
        session.add(charge)
        session.commit()
        session.refresh(charge)
        return "insertion réussie" 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")
def get_reservation_reserve_now(session : Session,page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        reservations  = session.exec(
            select(
                Reservation ,User,Connector,ChargePoint
            )
            .join(User,Reservation.user_id==User.id)
            .join(Connector, Reservation.connector_id == Connector.id)
            .join(ChargePoint, ChargePoint.id == Connector.charge_point_id)
            .order_by(desc(Reservation.id))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        count=session.exec(
            select(
                func.count(Reservation.id).label("nombre")
                 
            ).select_from(Reservation)).one()
        result=[]
        for reservation, user,connector,chargepoint in reservations:
            
            if reservation.etat==0:
                status="Annulé"
            if reservation.etat==1:
                status="Réservé"
            else:
                status="Terminé"
          
            checking = data_history_reservation(
                reservation_id=reservation.id,
                client = f"{user.first_name} {user.last_name}",
                date_reservation=reservation.date_reservation,
                date_expirate=reservation.expirate_date,
                connector_id=connector.id,
                charge_point_location=chargepoint.adresse,
                charge_point_vendors=chargepoint.charge_point_vendors,
                charge_point_id=chargepoint.id,
                status=status
            )
            result.append(checking)

        pagination.total_items = count
        return {"data": result, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def create_history(reserve:create_history_reservation, session : Session):
    try:
        charge : History_reservation = History_reservation(tag_id=reserve.tag_id,date_utilisation=reserve.date_utilisation,connector_id=reserve.connector_id,etat=reserve.etat)
        session.add(charge)
        session.commit()
        session.refresh(charge)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def update_reservation_etat(reservation_id:int,session:Session):
    try:
        reserve = session.exec(
            select(Reservation)
            .where(
               Reservation.id==reservation_id
            )
        ).first()
        if reserve is None:
            return 'Pas de reservation'
        reserve.etat=0
        session.add(reserve)
        session.commit()
        session.refresh(reserve)
        return "Modification réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
def update_history_etat(history_id:int,session:Session):
    try:
        reserve = session.exec(
            select(History_reservation)
            .where(
               History_reservation.id==history_id
            )
        ).first()
        if reserve is None:
            return 'Pas de reservation'
        reserve.etat=0
        session.add(reserve)
        session.commit()
        session.refresh(reserve)
        return "Modification réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
def take_reservation(charge_point_id: str, date_utilisation: datetime, session: Session):#reservation pas annulé
    try:
        reserve = session.exec(
            select(Reservation)
            .join(Connector, Reservation.connector_id == Connector.id)
            .join(ChargePoint, ChargePoint.id == Connector.charge_point_id)
            .where(
                and_(
                    date_utilisation >= Reservation.date_reservation,
                    date_utilisation <= Reservation.expirate_date,
                    ChargePoint.id == charge_point_id,
                    Reservation.etat==1
                )
            )
        ).all()
        return reserve
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

def take_user_match_with_tag(tags:str,session:Session):
    try:
        user = session.exec(
            select(User)
            .join(Tag, User.id == Tag.user_id)
            .where(
                Tag.tag==tags
            )
        ).first()
        return user
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
def check_reservation(date_utilisation:datetime,tag:str,charge_point_id:str,session : Session):#prendre est ce que la transaction est une reservation ou pas
    try:
        reserve=take_reservation(charge_point_id=charge_point_id,date_utilisation=date_utilisation,session=session)
        user=take_user_match_with_tag(tags=tag,session=session)
        if reserve:
            for reservation in reserve:
                if date_utilisation >= reservation.date_reservation and date_utilisation <= reservation.expirate_date:
                    if user.id == reservation.user_id:
                        # Réservation valide
                        return {
                            "date_utilisation": date_utilisation,
                            "connector_id": reservation.connector_id,
                            "status": "Valid",
                            "is_reserved": True
                        }
                    else:
                        # Pas la bonne personne
                        return {
                            "date_utilisation": date_utilisation,
                            "connector_id": reservation.connector_id,
                            "status": "Not the right person",
                            "is_reserved": False
                        }
                elif date_utilisation > reservation.expirate_date:
                    # Trop tard pour la réservation
                    return {
                        "date_utilisation": date_utilisation,
                        "connector_id": reservation.connector_id,
                        "status": "Too late",
                        "is_reserved": False
                    }
            # Aucun cas ne correspond
            return {
                "date_utilisation": date_utilisation,
                "connector_id": reservation.connector_id,
                "status": "No match",
                "is_reserved": False
            }
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def take_history_match_with_reservation(date_reservation:datetime,expirate_date:datetime,connector_id:str,session:Session):#prendre tous les history reservation associés au reservation
    try:
        reservation = session.exec(
            select(History_reservation)
            .where(
                and_(
                    History_reservation.date_utilisation>=date_reservation,
                    History_reservation.date_utilisation<=expirate_date,
                    History_reservation.connector_id==connector_id,
                    History_reservation.etat==1 
                )
            )
        ).first()
        return reservation
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
def check_reservation_api(session : Session,page: int = 1, number_items: int = 50):#prendre status des reservation
    try:
        pagination = Pagination(page=page, limit=number_items)
        reservations  = session.exec(
            select(
                Reservation ,User,Connector,ChargePoint
            )
            .join(User,Reservation.user_id==User.id)
            .join(Connector, Reservation.connector_id == Connector.id)
            .join(ChargePoint, ChargePoint.id == Connector.charge_point_id)
            .order_by(desc(Reservation.id))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        count=session.exec(
            select(
                func.count(Reservation.id).label("nombre")
                 
            ).select_from(Reservation)).one()
        result=[]
        for reservation, user,connector,chargepoint in reservations:
            check=take_history_match_with_reservation(date_reservation=reservation.date_reservation,expirate_date=reservation.expirate_date,connector_id=reservation.connector_id,session=session)
            if check is None:#s'il n'y a pas de history reservation correspondante
                now = datetime.now()
                if reservation.etat==0:
                    status="Annulé"
                else:
                    if reservation.expirate_date < now:
                        status = "Trop tard"
                    elif reservation.expirate_date > now > reservation.date_reservation:
                        status = "En cours"      
                    else:
                        status = "Réservé"
            else:
                if reservation.etat==2:
                    status="Terminé"
          

            checking = data_history_reservation(
                reservation_id=reservation.id,
                client = f"{user.first_name} {user.last_name}",
                date_reservation=reservation.date_reservation,
                date_expirate=reservation.expirate_date,
                connector_id=connector.id,
                charge_point_location=chargepoint.adresse,
                charge_point_vendors=chargepoint.charge_point_vendors,
                charge_point_id=chargepoint.id,
                status=status
            )
            result.append(checking)

        pagination.total_items = count
        return {"data": result, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}



def get_reservation_by_date(charge_point_id:str,day:date,session : Session,page: int = 1, number_items: int = 50):#recharche par jour
    try:
        pagination = Pagination(page=page, limit=number_items)
        query  = (select(Reservation, User, Connector, ChargePoint)
            .join(User, Reservation.user_id == User.id)
            .join(Connector, Reservation.connector_id == Connector.id)
            .join(ChargePoint, ChargePoint.id == Connector.charge_point_id))
        if charge_point_id is not None:
            query=query.where(ChargePoint.id==charge_point_id)
        if day is not None:
            query=query.where(func.date(Reservation.date_reservation) == day)
        query = query.order_by(desc(Reservation.id)).offset(pagination.offset).limit(pagination.limit)
        reservations=session.exec(query).all()
        c=(select(func.count(Reservation.id).label("nombre")))
        if charge_point_id is not None:
            c=c.where(ChargePoint.id==charge_point_id)
        if day is not None:
            c=c.where(func.date(Reservation.date_reservation) == day)
        count=session.exec(c).first()
        result=[]
        for reservation, user,connector,chargepoint in reservations:
            check=take_history_match_with_reservation(date_reservation=reservation.date_reservation,expirate_date=reservation.expirate_date,connector_id=reservation.connector_id,session=session)
            if check is None:#s'il n'y a pas de history reservation correspondante
                now = datetime.now()
                if reservation.etat==0:
                    status="Annulé"
                else:
                    if reservation.expirate_date < now:
                        status = "Trop tard"
                    elif reservation.expirate_date > now > reservation.date_reservation:
                        status = "En cours"      
                    else:
                        status = "Réservé"
            else:
                if reservation.etat==2:
                    status="Terminé"
          

            checking = data_history_reservation(
                reservation_id=reservation.id,
                client = f"{user.first_name} {user.last_name}",
                date_reservation=reservation.date_reservation,
                date_expirate=reservation.expirate_date,
                connector_id=connector.id,
                charge_point_location=chargepoint.adresse,
                charge_point_vendors=chargepoint.charge_point_vendors,
                charge_point_id=chargepoint.id,
                status=status
            )
            result.append(checking)

        pagination.total_items = count
        return {"data": result, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

    


    
    
    