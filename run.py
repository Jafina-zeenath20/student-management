from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import student_routes, attendance_routes
from app.models.database import Base, engine
from app.models import models
import os

# ✅ Step 1: Create tables first
Base.metadata.create_all(bind=engine)

# ✅ Step 2: Seed database (safe way)
def seed_database():
    from app.models.database import SessionLocal
    from app.models.models import Centre, Staff

    db = SessionLocal()

    # Check if already seeded
    if db.query(Centre).first():
        db.close()
        return

    # Add centres
    centres = ["Centre A", "Centre B", "Centre C"]
    for c in centres:
        db.add(Centre(name=c))
    db.commit()

    # Add staff
    db.add_all([
        Staff(name="Alice", centre_id=1),
        Staff(name="Bob", centre_id=1),
        Staff(name="John", centre_id=2),
        Staff(name="Mary", centre_id=3),
    ])
    db.commit()

    db.close()

# Run seed
seed_database()

# ✅ FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(student_routes.router)
app.include_router(attendance_routes.router)