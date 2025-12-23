import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    versions = relationship("FormVersion", back_populates="form", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="form")

class FormVersion(Base):
    __tablename__ = "form_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Store the definition as JSON
    schema_json = Column(JSON, default=dict)
    rules_json = Column(JSON, default=list)
    formulas_json = Column(JSON, default=list)
    pdf_template = Column(String, nullable=True) # HTML/Jinja Template
    webhook_url = Column(String, nullable=True) # n8n Webhook
    
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    form = relationship("Form", back_populates="versions")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    raw_data = Column(JSON, default=dict)
    computed_data = Column(JSON, default=dict)
    pdf_url = Column(String, nullable=True)
    
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    form = relationship("Form", back_populates="submissions")
    
    form_version_id = Column(Integer, ForeignKey("form_versions.id"), nullable=False)
    form_version = relationship("FormVersion")
