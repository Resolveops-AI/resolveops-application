import os
import uuid
import datetime
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Expects a standard PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

class Artifact(Base):
    __tablename__ = 'artifacts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(255), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False) # e.g., 'architecture', 'rca', 'report'
    blob_container = Column(String(255), nullable=False)
    blob_path = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="CREATED")

engine = None
SessionLocal = None

def init_pg_db():
    global engine, SessionLocal
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not set. PostgreSQL artifact storage will not be available.")
        return
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("PostgreSQL artifacts table initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize PostgreSQL DB: {e}")

def get_db():
    if not SessionLocal:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
