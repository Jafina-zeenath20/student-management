from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import StringIO
import csv
from datetime import date
from app.models.database import SessionLocal
from app.models.models import Student, Attendance, Fee
from app.routes.auth_routes import get_current_user
from app.services.student_service import get_all_students
from app.services.attendance_service import get_by_date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Export Students to CSV
@router.get("/export/students")
def export_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    students = get_all_students(db)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(["ID", "Name", "Grade", "Parent Contact", "Centre", "Staff", "Date of Birth"])
    
    # Data
    for student in students:
        writer.writerow([
            student.id,
            student.name,
            student.grade,
            student.parent_contact,
            student.centre.name if student.centre else "—",
            student.staff.name if student.staff else "—",
            student.dob.strftime("%Y-%m-%d") if student.dob else "—"
        ])
    
    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"}
    )

# ✅ Export Attendance Report by Date
@router.get("/export/attendance")
def export_attendance(
    selected_date: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    selected_date_obj = date.fromisoformat(selected_date) if selected_date else date.today()
    
    records = get_by_date(db, selected_date_obj)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(["Date", "Student", "Grade", "Centre", "Staff", "Status"])
    
    # Data
    for record in records:
        writer.writerow([
            record.date.strftime("%Y-%m-%d"),
            record.student.name if record.student else "—",
            record.student.grade if record.student else "—",
            record.student.centre.name if record.student and record.student.centre else "—",
            record.student.staff.name if record.student and record.student.staff else "—",
            record.status
        ])
    
    # Prepare response
    output.seek(0)
    filename = f"attendance_{selected_date_obj.strftime('%Y-%m-%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ✅ Export Fee Report
@router.get("/export/fees")
def export_fees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    fees = db.query(Fee).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(["Student", "Month", "Amount", "Status", "Paid Date"])
    
    # Data
    for fee in fees:
        writer.writerow([
            fee.student.name if fee.student else "—",
            fee.month,
            fee.amount,
            fee.status,
            fee.paid_date.strftime("%Y-%m-%d") if fee.paid_date else "—"
        ])
    
    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fees_report.csv"}
    )
