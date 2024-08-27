# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the API"}


from fastapi import FastAPI, Depends, APIRouter
from core.database import init_db, get_session
# router
from api.routes.routes import routers
app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()

# ROUTES
app.include_router(routers)

# with Session(engine) as session:
#     # Create sample data
#     charge_point = elecdis_models.ChargePoint(status="active")
#     session.add(charge_point)
#     session.commit()
#     session.refresh(charge_point)
#     connector = elecdis_models.Connector(charge_point_id=charge_point.id, connector_type="Type2")
#     session.add(connector)
#     session.commit()
#     session.refresh(connector)
#     tariff_group = elecdis_models.TariffGroup(name="Standard", new_column=1)
#     session.add(tariff_group)
#     session.commit()
#     session.refresh(tariff_group)
#     payment_method = elecdis_models.PaymentMethod()
#     session.add(payment_method)
#     session.commit()
#     session.refresh(payment_method)
#
#     user_group = elecdis_models.UserGroup(name="Admin")
#     session.add(user_group)
#     session.commit()
#     session.refresh(user_group)
#     partner = elecdis_models.Partner(name="Partner A")
#     session.add(partner)
#     session.commit()
#     session.refresh(partner)
#     contract = elecdis_models.Contract(partner_id=partner.id, circuit_id=1, start_date=date.today(), end_date=date.today())
#     session.add(contract)
#     session.commit()
#     session.refresh(contract)
#     tariff = elecdis_models.Tariff(name="Basic", tariff_group_id=tariff_group.id)
#     session.add(tariff)
#     session.commit()
#     session.refresh(tariff)
#
#     subscription = elecdis_models.Subscription(type_subscription="Premium")
#     session.add(subscription)
#     session.commit()
#     session.refresh(subscription)
#
#     user = elecdis_models.User(first_name="John", last_name="Doe", email="john.doe@example.com", password="password", id_user_group=user_group.id, id_subscription=subscription.id)
#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     payment_method_user = elecdis_models.PaymentMethodUser(id_payment_method=payment_method.id, id_user=1)
#     session.add(payment_method_user)
#     session.commit()
#     session.refresh(payment_method_user)
#     session_data = elecdis_models.Session(start_time=datetime.utcnow(), end_time=datetime.utcnow(), connector_id=connector.id, user_id=user.id)
#     session.add(session_data)
#     session.commit()
#     session.refresh(session_data)
#     transaction = elecdis_models.Transaction(session_id=session_data.id, amount=100.0, timestamp=datetime.utcnow())
#     session.add(transaction)
#     session.commit()
#     session.refresh(transaction)
#     tariff_snapshot = elecdis_models.TariffSnapshot(tariff_id=tariff.id, effective_date=date.today(), session_id=session_data.id)
#     session.add(tariff_snapshot)
#     session.commit()
#     session.refresh(tariff_snapshot)
#
#     tag = elecdis_models.Tag(user_id=user.id, tag="VIP")
#     session.add(tag)
#     session.commit()
#     session.refresh(tag)



