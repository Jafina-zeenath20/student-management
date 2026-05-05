from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import Centre, Staff, Student
from app.services.student_service import create_student, get_all_students, get_staff_by_centre, search_students, get_paginated_students
from app.services.attendance_service import get_attendance_stats
from app.routes.auth_routes import get_current_user, require_admin
from app.utils.validators import validate_student_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ FIXED DASHBOARD ROUTE with PAGINATION and ROLE-BASED ACCESS
@router.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    search: str = Query(None),
    centre_id: int = Query(None),
    staff_id: int = Query(None),
    grade: str = Query(None),
    page: int = Query(1, ge=1)
):
    # Staff can only see their own students
    if current_user["role"] == "staff" and current_user["staff_id"]:
        staff_id = current_user["staff_id"]
    
    students, total_pages = get_paginated_students(
        db, search, centre_id, staff_id, grade, page, per_page=10
    )
    
    centres = db.query(Centre).all()
    staff_list = db.query(Staff).all() if not centre_id else db.query(Staff).filter(Staff.centre_id == centre_id).all()
    attendance_stats = get_attendance_stats(db)
    
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "students": students,
            "centres": centres,
            "staff_list": staff_list,
            "search": search,
            "centre_id": centre_id,
            "staff_id": staff_id,
            "grade": grade,
            "page": page,
            "total_pages": total_pages,
            "attendance_stats": attendance_stats
        }
    )

# Add student page (Admin only)
@router.get("/add-student")
def add_student_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    centres = db.query(Centre).all()
    return templates.TemplateResponse(
        request,
        "add_student.html",
        {
            "centres": centres,
            "selected_centre": centres[0].id if centres else None,
            "selected_staff": None,
            "error": None
        }
    )

# Add student POST (Admin only)
@router.post("/add-student")
def add_student(
    request: Request,
    name: str = Form(...),
    grade: str = Form(...),
    parent_contact: str = Form(...),
    centre_id: int = Form(...),
    staff_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Validate data
    validation = validate_student_data(name, grade, parent_contact, parent_contact)
    if not validation["valid"]:
        centres = db.query(Centre).all()
        return templates.TemplateResponse(
            request,
            "add_student.html",
            {
                "centres": centres,
                "selected_centre": centre_id,
                "selected_staff": staff_id,
                "error": " | ".join(validation["errors"])
            }
        )
    
    # Check for duplicate phone
    existing = db.query(Student).filter(Student.parent_contact == parent_contact).first()
    if existing:
        centres = db.query(Centre).all()
        return templates.TemplateResponse(
            request,
            "add_student.html",
            {
                "centres": centres,
                "selected_centre": centre_id,
                "selected_staff": staff_id,
                "error": "A student with this phone number already exists"
            }
        )
    
    try:
        create_student(db, {
            "name": name,
            "grade": grade,
            "parent_contact": parent_contact,
            "centre_id": centre_id,
            "staff_id": staff_id
        })
        return RedirectResponse("/?success=Student added successfully", status_code=303)

    except Exception as e:
        centres = db.query(Centre).all()
        return templates.TemplateResponse(
            request,
            "add_student.html",
            {
                "centres": centres,
                "selected_centre": centre_id,
                "selected_staff": staff_id,
                "error": str(e)
            }
        )

# API to fetch staff by centre
@router.get("/staff/{centre_id}")
def get_staff(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    staff = get_staff_by_centre(db, centre_id)
    return [{"id": s.id, "name": s.name} for s in staff]