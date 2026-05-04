from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import student_routes, attendance_routes
from app.models.database import Base, engine
from app.models import models

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(student_routes.router)
app.include_router(attendance_routes.router)