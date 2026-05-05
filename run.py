from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import student_routes, attendance_routes
from app.models.database import Base, engine, SessionLocal
from app.models.models import Centre, Staff
from app.models import models

# Step 1: Create tables
Base.metadata.create_all(bind=engine)

# Step 2: Seed database properly
def seed_database():
    db = SessionLocal()

    # 🔥 IMPORTANT: Check BOTH tables
    if db.query(Centre).count() > 0 and db.query(Staff).count() > 0:
        db.close()
        return

    # Clear existing (safe reset)
    db.query(Staff).delete()
    db.query(Centre).delete()
    db.commit()

    # Add centres
    centres = ["Centre A", "Centre B", "Centre C"]
    centre_objects = []

    for c in centres:
        centre = Centre(name=c)
        db.add(centre)
        centre_objects.append(centre)

    db.commit()

    # Add staff (linked correctly)
    db.add_all([
        Staff(name="Alice", centre_id=centre_objects[0].id),
        Staff(name="Bob", centre_id=centre_objects[0].id),
        Staff(name="John", centre_id=centre_objects[1].id),
        Staff(name="Mary", centre_id=centre_objects[2].id),
    ])

    db.commit()
    db.close()

# Run seed
seed_database()

# App
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(student_routes.router)
app.include_router(attendance_routes.router)