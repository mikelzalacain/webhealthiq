import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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

HISTORY_LIMITS = {
    "free": 10,
    "pro": 100,
    "agency": 500,
}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    company = Column(String(120), nullable=True)
    brand_name = Column(String(120), nullable=True)
    brand_primary = Column(String(16), nullable=True)
    terms_accepted_at = Column(DateTime, nullable=True)
    plan = Column(String(32), nullable=False, default="free")
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usages = relationship("UsageMonth", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )


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
    lang = Column(String(8), nullable=True)
    result_json = Column(Text, nullable=True)
    insights_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audits")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="reset_tokens")


def _table_columns(conn, dialect: str, table: str) -> set[str]:
    # table is an internal identifier only (never user input)
    if dialect == "sqlite":
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
        return {r[1] for r in rows}
    rows = conn.exec_driver_sql(
        "SELECT column_name FROM information_schema.columns "
        f"WHERE table_name = '{table}'"
    ).fetchall()
    return {r[0] for r in rows}


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Lightweight migrations for existing DBs (SQLite/Postgres).
    with engine.begin() as conn:
        dialect = engine.dialect.name

        user_cols = _table_columns(conn, dialect, "users")
        user_alters = []
        if "full_name" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN full_name VARCHAR(120)")
        if "company" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN company VARCHAR(120)")
        if "terms_accepted_at" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMP")
        if "brand_name" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN brand_name VARCHAR(120)")
        if "brand_primary" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN brand_primary VARCHAR(16)")
        if "stripe_customer_id" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)")
        if "stripe_subscription_id" not in user_cols:
            user_alters.append("ALTER TABLE users ADD COLUMN stripe_subscription_id VARCHAR(255)")
        for stmt in user_alters:
            conn.exec_driver_sql(stmt)

        audit_cols = _table_columns(conn, dialect, "audit_logs")
        if audit_cols:  # table exists
            audit_alters = []
            if "lang" not in audit_cols:
                audit_alters.append("ALTER TABLE audit_logs ADD COLUMN lang VARCHAR(8)")
            if "result_json" not in audit_cols:
                audit_alters.append("ALTER TABLE audit_logs ADD COLUMN result_json TEXT")
            if "insights_json" not in audit_cols:
                audit_alters.append("ALTER TABLE audit_logs ADD COLUMN insights_json TEXT")
            for stmt in audit_alters:
                conn.exec_driver_sql(stmt)


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


def history_limit(plan: str) -> int:
    return HISTORY_LIMITS.get(plan or "free", HISTORY_LIMITS["free"])
