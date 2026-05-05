from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import User
from app.utils.auth import verify_password, hash_password
from app.utils.validators import validate_credentials

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Login Page
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None}
    )

# ✅ Login POST
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate input
    error = validate_credentials(username, password)
    if error:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": error}
        )
    
    # Query user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"}
        )
    
    # Set session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    request.session["staff_id"] = user.staff_id
    
    return RedirectResponse("/", status_code=303)

# ✅ Logout
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

# ✅ Dependency to check authentication
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return {
        "user_id": user_id,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "staff_id": request.session.get("staff_id")
    }

# ✅ Check if admin
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ✅ Check if staff or admin
def require_staff(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    return current_user
