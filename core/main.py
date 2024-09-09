from datetime import datetime

from fastapi import FastAPI

from api.mail.email_model import Email_model
from api.transaction.Transaction_models import Session_create, Session_update
from api.transaction.Transaction_service import create_session_service, update_session_service_on_stopTransaction
from core.database import init_db, get_session
# router
from api.routes.routes import routers

app = FastAPI()



@app.on_event("startup")
def on_startup():
    init_db()

# ROUTES
app.include_router(routers)

# print("update session ")
# session_data:Session_create = Session_create(start_time="2021-10-10 10:00:00",end_time="2021-10-10 12:00:00",connector_id="1",user_tag="123",metter_start=20)
#
# # create_session_service(session=next(get_session()), session_data=session_data)
#
# session_update_data = Session_update(
#     end_time="2023-10-10 10:00:00",
#     metter_stop=20,
#     transaction_id=1
# )
# print(update_session_service_on_stopTransaction(session=next(get_session()), session_data=session_update_data))


