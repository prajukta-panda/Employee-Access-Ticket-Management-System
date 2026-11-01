from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.tickets import router as tickets_router
from routers.admin import router as admin_router
app=FastAPI()

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(admin_router)