from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import Mark, Student
from app.routes.auth_routes import get_current_user, require_admin
from app.utils.validators import validate_mark_data
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Marks Page (Admin only)
@router.get("/marks")
def marks_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
    student_id: int = Query(None),
    subject: str = Query(None)
):
    query = db.query(Mark)
    
    if student_id:
        query = query.filter(Mark.student_id == student_id)
    
    if subject:
        query = query.filter(Mark.subject.ilike(f"%{subject}%"))
    
    marks = query.all()
    students = db.query(Student).all()
    
    # Get rankings
    rankings = get_student_rankings(db)
    
    return templates.TemplateResponse(
        request,
        "marks.html",
        {
            "marks": marks,
            "students": students,
            "student_id": student_id,
            "subject": subject,
            "rankings": rankings
        }
    )

# ✅ Add Mark
@router.post("/marks/add")
def add_mark(
    request: Request,
    student_id: int = Form(...),
    subject: str = Form(...),
    marks: float = Form(...),
    total_marks: float = Form(100),
    test_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Validate data
    validation = validate_mark_data(subject, marks, total_marks)
    if not validation["valid"]:
        return RedirectResponse("/marks?error=" + " | ".join(validation["errors"]), status_code=303)
    
    test_date_obj = date.fromisoformat(test_date)
    
    mark = Mark(
        student_id=student_id,
        subject=subject,
        marks=marks,
        total_marks=total_marks,
        test_date=test_date_obj
    )
    db.add(mark)
    db.commit()
    
    return RedirectResponse("/marks?success=Mark added successfully", status_code=303)

# ✅ Get Student Rankings (based on average marks)
def get_student_rankings(db: Session):
    """
    Calculate student rankings based on average marks across all tests
    Returns: list of (student, average_marks, rank)
    """
    from sqlalchemy import func
    
    # Query average marks per student
    query = db.query(
        Student.id,
        Student.name,
        func.avg(Mark.marks / Mark.total_marks * 100).label('avg_percentage')
    ).outerjoin(Mark).group_by(Student.id, Student.name).order_by(
        func.avg(Mark.marks / Mark.total_marks * 100).desc()
    )
    
    results = query.all()
    
    rankings = []
    for rank, (student_id, name, avg_percentage) in enumerate(results, 1):
        rankings.append({
            'rank': rank,
            'student_id': student_id,
            'name': name,
            'average': round(avg_percentage or 0, 2)
        })
    
    return rankings
