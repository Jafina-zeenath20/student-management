from app.models.database import Base, engine, SessionLocal
from app.models.models import Centre, Staff

Base.metadata.create_all(bind=engine)
db = SessionLocal()

centres = ["Centre A", "Centre B", "Centre C"]

for c in centres:
    if not db.query(Centre).filter_by(name=c).first():
        db.add(Centre(name=c))

db.commit()

if not db.query(Staff).first():
    db.add_all([
        Staff(name="Alice", centre_id=1),
        Staff(name="Bob", centre_id=1),
        Staff(name="John", centre_id=2),
        Staff(name="Mary", centre_id=3),
    ])
    db.commit()

print("Database ready")