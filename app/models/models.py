from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Centre(Base):
    __tablename__ = "centres"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    staff = relationship("Staff", back_populates="centre", lazy="selectin")
    students = relationship("Student", back_populates="centre", lazy="selectin")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    centre_id = Column(Integer, ForeignKey("centres.id"), nullable=False)
    centre = relationship("Centre", back_populates="staff")
    students = relationship("Student", back_populates="staff", lazy="selectin")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    grade = Column(String, nullable=False)
    parent_contact = Column(String, nullable=False, unique=True)  # Prevent duplicates
    notes = Column(String, nullable=True)
    centre_id = Column(Integer, ForeignKey("centres.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    centre = relationship("Centre", back_populates="students")
    staff = relationship("Staff", back_populates="students")
    attendance = relationship("Attendance", back_populates="student", lazy="selectin")
    fees = relationship("Fee", back_populates="student", lazy="selectin")
    marks = relationship("Mark", back_populates="student", lazy="selectin")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    student = relationship("Student", back_populates="attendance")

    __table_args__ = (
        UniqueConstraint("student_id", "date", name="unique_attendance"),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")  # 'admin' or 'staff'
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    staff = relationship("Staff")

class Fee(Base):
    __tablename__ = "fees"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # e.g., "January 2026"
    status = Column(String, default="Pending")  # "Pending" or "Paid"
    paid_date = Column(Date, nullable=True)
    student = relationship("Student", back_populates="fees")
    
    __table_args__ = (
        UniqueConstraint("student_id", "month", name="unique_fee_month"),
    )

class Mark(Base):
    __tablename__ = "marks"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String, nullable=False)  # e.g., "Mathematics", "English"
    marks = Column(Float, nullable=False)
    total_marks = Column(Float, default=100, nullable=False)
    test_date = Column(Date, nullable=False)
    student = relationship("Student", back_populates="marks")