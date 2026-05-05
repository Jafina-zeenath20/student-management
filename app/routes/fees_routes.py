from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import Fee, Student
from app.routes.auth_routes import get_current_user, require_admin
from app.utils.validators import validate_fee_data
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Fee Management Page (Admin only)
@router.get("/fees")
def fees_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
    student_id: int = Query(None),
    status: str = Query(None)
):
    query = db.query(Fee)
    
    if student_id:
        query = query.filter(Fee.student_id == student_id)
    
    if status:
        query = query.filter(Fee.status == status)
    
    fees = query.all()
    students = db.query(Student).all()
    
    return templates.TemplateResponse(
        request,
        "fees.html",
        {
            "fees": fees,
            "students": students,
            "student_id": student_id,
            "status": status
        }
    )

# ✅ Add Fee
@router.post("/fees/add")
def add_fee(
    request: Request,
    student_id: int = Form(...),
    amount: float = Form(...),
    month: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Validate data
    validation = validate_fee_data(amount, month)
    if not validation["valid"]:
        return RedirectResponse("/fees?error=" + " | ".join(validation["errors"]), status_code=303)
    
    # Check if fee already exists for this month
    existing = db.query(Fee).filter(
        Fee.student_id == student_id,
        Fee.month == month
    ).first()
    
    if existing:
        return RedirectResponse("/fees?error=Fee already exists for this month", status_code=303)
    
    fee = Fee(student_id=student_id, amount=amount, month=month, status="Pending")
    db.add(fee)
    db.commit()
    
    return RedirectResponse("/fees?success=Fee added successfully", status_code=303)

# ✅ Mark Fee as Paid
@router.post("/fees/{fee_id}/mark-paid")
def mark_fee_paid(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    
    if fee:
        fee.status = "Paid"
        fee.paid_date = date.today()
        db.commit()
    
    return RedirectResponse("/fees?success=Fee marked as paid", status_code=303)
