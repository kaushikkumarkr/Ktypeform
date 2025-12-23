from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.form import Form, FormVersion, Submission
from app.models.user import User
from app.schemas import submission as sub_schemas
from app.core.db import get_db
from app.core.logic.validation import validate_submission, ValidationError
from app.core.logic.rules import evaluate_rules
from app.core.logic.formulas import process_formulas
from app.core.pdf_service import pdf_service
from app.core.webhook_service import webhook_service

router = APIRouter()

@router.get("/public/forms/{slug}", response_model=dict)
def get_public_form_schema(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Public Endpoint: Get form schema (latest version)
    """
    form = db.query(Form).filter(Form.slug == slug).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Get latest version
    version = db.query(FormVersion).filter(FormVersion.form_id == form.id).order_by(FormVersion.version_number.desc()).first()
    
    if not version:
         raise HTTPException(status_code=404, detail="Form has no versions")
         
    return {
        "title": form.title,
        "slug": form.slug,
        "schema": version.schema_json,
        "rules": version.rules_json,
        "version": version.version_number
    }

@router.post("/public/{slug}/submit", response_model=dict)
def create_public_submission(
    slug: str,
    submission_in: sub_schemas.PublicSubmissionCreate,
    db: Session = Depends(get_db)
):
    """
    Public Endpoint: Submit data for a form.
    """
    # 1. Find Form
    form = db.query(Form).filter(Form.slug == slug).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    # 2. Find Latest Published Version (or just latest for MVP debugging?)
    # MVP: Find latest published. If none, fail.
    # version = db.query(FormVersion).filter(
    #     FormVersion.form_id == form.id, 
    #     FormVersion.is_published == True
    # ).order_by(FormVersion.version_number.desc()).first()
    
    # FOR MVP DEV: Allow using latest implementation even if not published, 
    # OR we force user to publish. Let's force publish workflow logic later,
    # for now take the absolute latest version.
    version = db.query(FormVersion).filter(FormVersion.form_id == form.id).order_by(FormVersion.version_number.desc()).first()
    
    if not version:
         raise HTTPException(status_code=400, detail="Form has no versions configured")

    input_data = submission_in.answers
    
    # 3. Validate
    try:
        validate_submission(version.schema_json, input_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"field": e.field_id, "message": e.message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation Error: {str(e)}")
        
    # 4. Rules (Visibility) - For MVP we assume all data sent is intentional.
    # We could run this and strip hidden fields.
    # visibility = evaluate_rules(version.rules_json, input_data)
    
    # 5. Formulas
    try:
        computed = process_formulas(version.formulas_json, input_data)
    except Exception as e:
         raise HTTPException(status_code=422, detail=f"Formula Error: {str(e)}")
    
    # 6. Save
    submission = Submission(
        form_id=form.id,
        form_version_id=version.id,
        raw_data=input_data,
        computed_data=computed
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # 7. PDF Generation
    pdf_url = None
    if version.pdf_template:
        try:
            # Prepare data for template: raw + computed
            tpl_data = {**input_data, **computed}
            html = pdf_service.render_html(version.pdf_template, tpl_data)
            pdf_bytes = pdf_service.generate_pdf_bytes(html)
            pdf_url = pdf_service.upload_pdf(pdf_bytes)
            
            # Update submission
            submission.pdf_url = pdf_url # Need to add this column too!
            db.add(submission)
            db.commit()
        except Exception as e:
            print(f"PDF Gen failed: {e}")
            # Non-blocking failure for MVP
            
    # 8. Trigger Logic (n8n)
    if version.webhook_url:
        payload = {
            "event": "submission.created",
            "form_id": form.id,
            "submission_id": submission.id,
            "data": submission.raw_data,
            "computed": submission.computed_data,
            "pdf_url": pdf_url
        }
        webhook_service.trigger_webhook(version.webhook_url, payload)
    
    return {"id": submission.id, "message": "Submission received", "pdf_url": pdf_url}

@router.get("/{form_id}/submissions", response_model=List[sub_schemas.Submission])
def read_submissions(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Admin Endpoint: List submissions for a form.
    """
    # Verify ownership
    form = db.query(Form).filter(Form.id == form_id, Form.org_id == current_user.org_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    submissions = db.query(Submission).filter(Submission.form_id == form_id).offset(skip).limit(limit).all()
    return submissions
