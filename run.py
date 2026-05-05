from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from app.routes import student_routes, attendance_routes, auth_routes
from app.models.database import Base, engine, SessionLocal
from app.models.models import Centre, Staff, User
from app.utils.auth import hash_password
from app.models import models

# Step 1: Create tables
Base.metadata.create_all(bind=engine)

# Step 2: Seed database properly
def seed_database():
    db = SessionLocal()

    # Check if already seeded
    if db.query(Centre).count() > 0 and db.query(Staff).count() > 0 and db.query(User).count() > 0:
        db.close()
        return

    # Clear existing (safe reset)
    db.query(Staff).delete()
    db.query(Centre).delete()
    db.query(User).delete()
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
    staff_objects = [
        Staff(name="Alice", centre_id=centre_objects[0].id),
        Staff(name="Bob", centre_id=centre_objects[0].id),
        Staff(name="John", centre_id=centre_objects[1].id),
        Staff(name="Mary", centre_id=centre_objects[2].id),
    ]
    
    db.add_all(staff_objects)
    db.commit()

    # Add demo users
    db.add_all([
        User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
            staff_id=None
        ),
        User(
            username="staff",
            password_hash=hash_password("staff123"),
            role="staff",
            staff_id=staff_objects[0].id
        ),
    ])
    db.commit()
    db.close()

# Run seed
seed_database()

# App
app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

# Custom middleware to redirect unauthenticated users
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Allow these routes without authentication
        allowed_paths = ["/login", "/static"]
        
        if any(request.url.path.startswith(path) for path in allowed_paths):
            return await call_next(request)
        
        # Check if user is authenticated
        if "user_id" not in request.session:
            return RedirectResponse("/login", status_code=303)
        
        return await call_next(request)

app.add_middleware(AuthMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(attendance_routes.router)

# Import new routers
from app.routes import fees_routes, marks_routes, export_routes
app.include_router(fees_routes.router)
app.include_router(marks_routes.router)
app.include_router(export_routes.router)