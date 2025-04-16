from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="employee")
    is_active = Column(Boolean, default=True)
    is_initial_password = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    department = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    availability = Column(String, nullable=True)
    working_hours = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    photo_thumb = Column(String, nullable=True)
    projects = Column(JSON, nullable=True)
    vk_link = Column(String, nullable=True)
    telegram_link = Column(String, nullable=True)
    skype_link = Column(String, nullable=True)
    whatsapp_link = Column(String, nullable=True)