from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.core.db import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tier = Column(String, default="free")
    
    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default=UserRole.ADMIN) 
    
    org_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")
