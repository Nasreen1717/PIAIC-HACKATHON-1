"""User and authentication-related database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User account model with authentication credentials."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    background = relationship("UserBackground", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"


class UserBackground(Base):
    """User questionnaire and background information."""
    __tablename__ = "user_backgrounds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    software_background = Column(String(255), nullable=True)
    hardware_background = Column(String(255), nullable=True)
    ros_experience = Column(String(255), nullable=True)
    python_level = Column(String(255), nullable=True)  # beginner, intermediate, advanced
    learning_goal = Column(String(500), nullable=True)
    available_hardware = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="background")

    def __repr__(self):
        return f"<UserBackground(user_id={self.user_id}, python_level={self.python_level})>"
