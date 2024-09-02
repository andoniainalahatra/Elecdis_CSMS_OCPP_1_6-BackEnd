from fastapi import FastAPI
from core.database import init_db
# router
from api.routes.routes import routers

app = FastAPI()



@app.on_event("startup")
def on_startup():
    init_db()

# ROUTES
app.include_router(routers)



