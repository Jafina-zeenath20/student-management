import hashlib
from sqlalchemy.orm import Session
from app.models.models import User

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash

def create_user(db: Session, username: str, password: str, role: str = "staff", staff_id: int = None):
    """Create a new user."""
    if db.query(User).filter(User.username == username).first():
        raise ValueError("Username already exists")
    
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        staff_id=staff_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user and return user object if valid."""
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None
