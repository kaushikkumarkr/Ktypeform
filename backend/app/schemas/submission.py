from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SubmissionBase(BaseModel):
    raw_data: Dict[str, Any]

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    id: int
    created_at: datetime
    form_id: int
    form_version_id: int
    computed_data: Dict[str, Any] = {}
    pdf_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PublicSubmissionCreate(BaseModel):
    answers: Dict[str, Any]
