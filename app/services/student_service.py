from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.models import Student, Staff

def create_student(db: Session, data):
    staff = db.query(Staff).filter(Staff.id == data["staff_id"]).first()

    if not staff:
        raise ValueError("Selected staff member was not found.")

    if staff.centre_id != data["centre_id"]:
        raise ValueError("Selected staff does not belong to the chosen centre.")

    student = Student(**data)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_all_students(db: Session):
    return db.query(Student).options(
        joinedload(Student.centre),
        joinedload(Student.staff)
    ).all()


def get_staff_by_centre(db: Session, centre_id: int):
    return db.query(Staff).filter(Staff.centre_id == centre_id).all()


# ✅ NEW FUNCTION (THIS FIXES YOUR ERROR)
def search_students(db: Session, search=None, centre_id=None, staff_id=None, grade=None):
    query = db.query(Student).options(
        joinedload(Student.centre),
        joinedload(Student.staff)
    )

    # 🔍 Search by name or phone
    if search:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.parent_contact.ilike(f"%{search}%")
            )
        )

    # 🎯 Filter by centre
    if centre_id:
        query = query.filter(Student.centre_id == centre_id)

    # 🎯 Filter by staff
    if staff_id:
        query = query.filter(Student.staff_id == staff_id)

    # 🎯 Filter by grade
    if grade:
        query = query.filter(Student.grade.ilike(f"%{grade}%"))

    return query.all()