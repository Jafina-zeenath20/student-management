from sqlalchemy.orm import Session, joinedload
from app.models.models import Attendance, Student
from datetime import date

# ✅ Create or update attendance
def mark_attendance(db: Session, student_id: int, status: str, attendance_date: date = None):
    if attendance_date is None:
        attendance_date = date.today()

    record = db.query(Attendance).filter_by(
        student_id=student_id,
        date=attendance_date
    ).first()

    if record:
        # update existing
        record.status = status
        db.commit()
        return

    new_record = Attendance(
        student_id=student_id,
        date=attendance_date,
        status=status
    )
    db.add(new_record)
    db.commit()


# ✅ Get attendance by date
def get_by_date(db: Session, selected_date):
    return db.query(Attendance).options(
        joinedload(Attendance.student).joinedload(Student.centre),
        joinedload(Attendance.student).joinedload(Student.staff)
    ).filter(Attendance.date == selected_date).all()


# ✅ FIX: Add missing function
def get_by_student(db: Session, student_id: int):
    return db.query(Attendance).options(
        joinedload(Attendance.student)
    ).filter(Attendance.student_id == student_id).all()


# ✅ Attendance analytics (already correct)
def get_attendance_stats(db: Session):
    from sqlalchemy import func

    stats = {}
    students = db.query(Student).all()

    for student in students:
        total = db.query(Attendance).filter(
            Attendance.student_id == student.id
        ).count()

        present = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.status == "Present"
        ).count()

        percentage = (present / total * 100) if total > 0 else 0

        stats[student.id] = {
            "student": student,
            "total": total,
            "present": present,
            "percentage": round(percentage, 1),
            "low_attendance": percentage < 75 and total > 0
        }

    return stats