import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{data_dir / 'webhealthiq.db'}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

PLAN_LIMITS = {
    "free": 5,
    "pro": 50,
    "agency": 200,
}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    plan = Column(String(32), nullable=False, default="free")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usages = relationship("UsageMonth", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class UsageMonth(Base):
    __tablename__ = "usage_months"
    __table_args__ = (UniqueConstraint("user_id", "year_month", name="uq_user_month"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    year_month = Column(String(7), nullable=False)  # YYYY-MM
    count = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="usages")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    overall_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audits")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_year_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def get_or_create_usage(db: Session, user: User) -> UsageMonth:
    ym = current_year_month()
    usage = (
        db.query(UsageMonth)
        .filter(UsageMonth.user_id == user.id, UsageMonth.year_month == ym)
        .first()
    )
    if usage is None:
        usage = UsageMonth(user_id=user.id, year_month=ym, count=0)
        db.add(usage)
        db.commit()
        db.refresh(usage)
    return usage


def plan_limit(plan: str) -> int:
    return PLAN_LIMITS.get(plan or "free", PLAN_LIMITS["free"])
