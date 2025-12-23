from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class FormVersionBase(BaseModel):
    schema_json: Dict[str, Any] = {}
    rules_json: List[Dict[str, Any]] = []
    formulas_json: List[Dict[str, Any]] = []
    pdf_template: Optional[str] = None
    webhook_url: Optional[str] = None
    is_published: bool = False

class FormVersionCreate(FormVersionBase):
    pass

class FormVersion(FormVersionBase):
    id: int
    version_number: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FormBase(BaseModel):
    title: str
    slug: str

class FormCreate(FormBase):
    pass

class Form(FormBase):
    id: int
    created_at: datetime
    org_id: int
    versions: List[FormVersion] = []
    
    model_config = ConfigDict(from_attributes=True)
