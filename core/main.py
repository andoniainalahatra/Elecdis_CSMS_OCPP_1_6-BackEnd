from datetime import datetime, timedelta

from fastapi import FastAPI

from api.auth.Auth_services import generate_keys
from api.mail.email_model import Email_model
from api.transaction.Transaction_models import Session_create, Session_update
from api.transaction.Transaction_service import create_session_service, update_session_service_on_stopTransaction, \
    create_default_transaction
from api.users.UserServices import create_default_admin_usergroup
from core.database import init_db, get_session
# router
from api.routes.routes import routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    session = next(get_session())
    create_default_admin_usergroup(session)
    create_default_transaction(session)
    # generate_keys()

# ROUTES



from pathlib import Path

# Get the current file's path
current_dir = Path(__file__).resolve()

# Navigate up to the project root (adjust the number of parents as needed)
root_dir = current_dir.parents[1]  # Adjust '1' depending on how many levels up the root is
dr=datetime.now() + timedelta(days=2)

print(dr.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
app.include_router(routers)

# print("update session ")
# session_data:Session_create = Session_create(start_time="2021-10-10 10:00:00",end_time="2021-10-10 12:00:00",connector_id="1",user_tag="123",metter_start=20)
#
# # create_session_service(session=next(get_session()), session_data=session_data)
#
# session_update_data = Session_update(
#     end_time="2024-09-23 14:25:09.792000",
#     metter_stop=58,
#     transaction_id=2
# )
# print(update_session_service_on_stopTransaction(session=next(get_session()), session_data=session_update_data))
# session_update_data = Session_update(
#     end_time="2024-09-26 07:29:43.537295",
#     metter_stop=15,
#     transaction_id=3
# )
# print(update_session_service_on_stopTransaction(session=next(get_session()), session_data=session_update_data))
# session_update_data = Session_update(
#     end_time="2024-09-26 10:56:04.555303",
#     metter_stop=79,
#     transaction_id=4
# )
# print(update_session_service_on_stopTransaction(session=next(get_session()), session_data=session_update_data))


