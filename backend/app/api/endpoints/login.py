from datetime import timedelta, datetime
from typing import Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token
from app.schemas import user as user_schemas

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Simple direct query authentication for MVP
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=Token)
def signup(
    user_in: user_schemas.UserCreate, 
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Register a new user and organization.
    """
    from app.models.user import Organization
    from app.schemas import user as user_schema
    
    # 1. Check if email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    # 2. Create Organization
    org = Organization(name=f"{user_in.email}'s Workspace", tier="free")
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # 3. Create User
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role="admin", # Creator is admin of their org
        org_id=org.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 4. Auto Login
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/invite")
def invite_user(
    email: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Invite a user to your organization.
    """
    from app.models.invite import OrganizationInvite
    from app.core.email_service import email_service
    
    # Check if already invited
    existing = db.query(OrganizationInvite).filter(
        OrganizationInvite.email == email, 
        OrganizationInvite.org_id == current_user.org_id,
        OrganizationInvite.status == "pending"
    ).first()
    
    if existing:
        return {"message": "User already invited", "token": existing.token} # Return token for testing convenience

    invite = OrganizationInvite(email=email, org_id=current_user.org_id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    # Send Email (Mock)
    # in real app: email_service.send_invite_email(email, invite.token)
    print(f"MOCK EMAIL: Invite sent to {email}. Link: http://localhost:3000/join?token={invite.token}")
    
    return {"message": "Invite sent", "token": invite.token}

class JoinRequest(BaseModel):
    token: str
    password: str

@router.post("/join", response_model=Token)
def join_organization(
    join_in: JoinRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Join an organization via invite token.
    """
    from app.models.invite import OrganizationInvite
    from app.models.user import User
    
    invite = db.query(OrganizationInvite).filter(OrganizationInvite.token == join_in.token, OrganizationInvite.status == "pending").first()
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    # Check if user already exists
    if db.query(User).filter(User.email == invite.email).first():
        raise HTTPException(status_code=400, detail="User already registered")

    # Create User
    user = User(
        email=invite.email,
        hashed_password=security.get_password_hash(join_in.password),
        role="editor", # Default role for invited members
        org_id=invite.org_id,
        is_active=True
    )
    db.add(user)
    
    invite.status = "accepted"
    db.commit()
    db.refresh(user)
    
    # Auto Login
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

# ==================== API Keys ====================
import secrets
from typing import List

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None
    
    class Config:
        from_attributes = True

@router.post("/api-keys")
def create_api_key(
    key_in: APIKeyCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate a new API Key. The raw key is returned ONLY ONCE.
    """
    from app.models.api_key import APIKey
    
    # Generate a secure random key
    raw_key = f"kf_{secrets.token_urlsafe(32)}"
    prefix = raw_key[:12]  # e.g., "kf_abc123..."
    key_hash = security.get_password_hash(raw_key)
    
    api_key = APIKey(
        name=key_in.name,
        key_hash=key_hash,
        prefix=prefix,
        org_id=current_user.org_id
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return {
        "id": api_key.id,
        "name": api_key.name,
        "prefix": api_key.prefix,
        "key": raw_key,  # Only time user sees the full key
        "created_at": api_key.created_at
    }

@router.get("/api-keys", response_model=List[APIKeyResponse])
def list_api_keys(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all API keys for the current user's organization.
    """
    from app.models.api_key import APIKey
    
    keys = db.query(APIKey).filter(APIKey.org_id == current_user.org_id).all()
    return keys

@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Revoke (delete) an API key.
    """
    from app.models.api_key import APIKey
    
    api_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.org_id == current_user.org_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    db.delete(api_key)
    db.commit()
    return {"message": "API Key revoked"}
