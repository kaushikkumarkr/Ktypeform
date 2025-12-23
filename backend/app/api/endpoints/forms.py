from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.form import Form, FormVersion
from app.models.user import User
from app.schemas import form as form_schemas
from app.core.db import get_db

router = APIRouter()

@router.get("/", response_model=List[form_schemas.Form])
def read_forms(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user_or_api_key),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve forms for the current user's organization.
    """
    forms = db.query(Form).filter(Form.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return forms

@router.post("/", response_model=form_schemas.Form)
def create_form(
    *,
    db: Session = Depends(get_db),
    form_in: form_schemas.FormCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new form.
    """
    form = Form(
        title=form_in.title,
        slug=form_in.slug,
        org_id=current_user.org_id
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    
    # Create initial version
    version = FormVersion(
        form_id=form.id,
        version_number=1,
        schema_json={},
        rules_json=[],
        formulas_json=[]
    )
    db.add(version)
    db.commit()
    db.refresh(form) # Refresh to load relationship
    
    return form

@router.get("/{form_id}", response_model=form_schemas.Form)
def read_form(
    *,
    db: Session = Depends(get_db),
    form_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get form by ID.
    """
    form = db.query(Form).filter(Form.id == form_id, Form.org_id == current_user.org_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

@router.post("/{form_id}/versions", response_model=form_schemas.FormVersion)
def create_form_version(
    *,
    db: Session = Depends(get_db),
    form_id: int,
    version_in: form_schemas.FormVersionCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new version for a form.
    """
    form = db.query(Form).filter(Form.id == form_id, Form.org_id == current_user.org_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    # Get last version number
    last_version = db.query(FormVersion).filter(FormVersion.form_id == form_id).order_by(FormVersion.version_number.desc()).first()
    new_version_number = (last_version.version_number + 1) if last_version else 1
    
    version = FormVersion(
        form_id=form_id,
        version_number=new_version_number,
        schema_json=version_in.schema_json,
        rules_json=version_in.rules_json,
        formulas_json=version_in.formulas_json,
        pdf_template=version_in.pdf_template,
        webhook_url=version_in.webhook_url,
        is_published=version_in.is_published
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
