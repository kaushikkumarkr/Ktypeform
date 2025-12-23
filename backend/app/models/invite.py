from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.db import Base

class OrganizationInvite(Base):
    __tablename__ = "organization_invites"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    token = Column(String, unique=True, index=True, default=lambda: uuid.uuid4().hex)
    status = Column(String, default="pending") # pending, accepted
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")
