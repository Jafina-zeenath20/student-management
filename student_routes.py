from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import Centre, Staff
from app.services.student_service import create_student, get_all_students, get_staff_by_centre, search_students
from app.services.attendance_service import get_attendance_stats

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ FIXED DASHBOARD ROUTE
@router.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    search: str = Query(None),
    centre_id: int = Query(None),
    staff_id: int = Query(None),
    grade: str = Query(None)
):
    students = search_students(db, search, centre_id, staff_id, grade)
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
            "attendance_stats": attendance_stats
        }
    )

# Add student page
@router.get("/add-student")
def add_student_page(request: Request, db: Session = Depends(get_db)):
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

# Add student POST
@router.post("/add-student")
def add_student(
    request: Request,
    name: str = Form(...),
    grade: str = Form(...),
    parent_contact: str = Form(...),
    centre_id: int = Form(...),
    staff_id: int = Form(...),
    db: Session = Depends(get_db)
):
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
def get_staff(centre_id: int, db: Session = Depends(get_db)):
    staff = get_staff_by_centre(db, centre_id)
    return [{"id": s.id, "name": s.name} for s in staff]