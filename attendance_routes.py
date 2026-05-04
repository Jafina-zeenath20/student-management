from fastapi import APIRouter, Depends, Request, Query, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date
from app.models.database import SessionLocal
from app.models.models import Student, Attendance
from app.services.attendance_service import mark_attendance, get_by_date, get_by_student

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Attendance Page
@router.get("/attendance")
def attendance_page(
    request: Request,
    db: Session = Depends(get_db),
    selected_date: str = Query(None)
):
    selected_date_obj = date.fromisoformat(selected_date) if selected_date else date.today()

    students = db.query(Student).options(
        joinedload(Student.centre),
        joinedload(Student.staff)
    ).all()

    return templates.TemplateResponse(
        request,
        "attendance.html",
        {
            "students": students,
            "selected_date": str(selected_date_obj)
        }
    )


# ✅ Mark Attendance
@router.post("/attendance")
async def mark(
    request: Request,
    db: Session = Depends(get_db),
    selected_date: str = Query(None)
):
    form = dict(await request.form())
    selected_date_obj = date.fromisoformat(selected_date) if selected_date else date.today()

    for key, value in form.items():
        if key.startswith("student_"):
            student_id = int(key.split("_")[1])
            mark_attendance(db, student_id, value, selected_date_obj)

    students = db.query(Student).options(
        joinedload(Student.centre),
        joinedload(Student.staff)
    ).all()

    return templates.TemplateResponse(
        request,
        "attendance.html",
        {
            "students": students,
            "selected_date": str(selected_date_obj),
            "message": f"Attendance for {selected_date_obj.strftime('%Y-%m-%d')} saved!"
        }
    )


# ✅ View Attendance
@router.get("/view-attendance")
def view_attendance(
    request: Request,
    db: Session = Depends(get_db),
    selected_date: str = Query(None)
):
    selected_date_obj = date.fromisoformat(selected_date) if selected_date else date.today()

    records = get_by_date(db, selected_date_obj)

    return templates.TemplateResponse(
        request,
        "view_attendance.html",
        {
            "records": records,
            "selected_date": str(selected_date_obj)
        }
    )


# ✅ Edit Attendance Page
@router.get("/edit-attendance/{student_id}/{selected_date}")
def edit_attendance_page(
    student_id: int,
    selected_date: str,
    request: Request,
    db: Session = Depends(get_db)
):
    selected_date_obj = date.fromisoformat(selected_date)

    student = db.query(Student).options(
        joinedload(Student.centre),
        joinedload(Student.staff)
    ).filter(Student.id == student_id).first()

    if not student:
        return RedirectResponse("/view-attendance", status_code=303)

    record = db.query(Attendance).filter_by(
        student_id=student_id,
        date=selected_date_obj
    ).first()

    return templates.TemplateResponse(
        request,
        "edit_attendance.html",
        {
            "student": student,
            "record": record,
            "selected_date": str(selected_date_obj),
            "current_status": record.status if record else "Present"
        }
    )


# ✅ FIXED: Update Attendance (MAIN FIX)
@router.post("/edit-attendance/{student_id}/{selected_date}")
def update_attendance(
    student_id: int,
    selected_date: str,
    request: Request,
    db: Session = Depends(get_db),
    status: str = Form(...)   # 🔥 FIXED HERE
):
    selected_date_obj = date.fromisoformat(selected_date)

    mark_attendance(db, student_id, status, selected_date_obj)

    return RedirectResponse(
        f"/view-attendance?selected_date={selected_date}",
        status_code=303
    )