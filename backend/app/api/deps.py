from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.models.user import User
from app.core import security
from app.core.config import settings
from app.core.db import get_db

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# Optional OAuth2 for endpoints that also accept API keys
reusable_oauth2_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False  # Makes it optional, returns None instead of 401
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.id == token_data).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_from_api_key(
    db: Session,
    api_key: str
) -> Optional[User]:
    """
    Validate API key and return the first admin user of the associated org.
    """
    from app.models.api_key import APIKey
    from datetime import datetime
    
    if not api_key or not api_key.startswith("kf_"):
        return None
    
    prefix = api_key[:12]
    keys = db.query(APIKey).filter(APIKey.prefix == prefix).all()
    
    for key in keys:
        if security.verify_password(api_key, key.key_hash):
            # Update last_used_at
            key.last_used_at = datetime.utcnow()
            db.commit()
            
            # Get admin user of org (or any user)
            user = db.query(User).filter(User.org_id == key.org_id).first()
            return user
    
    return None

from fastapi import Header

def get_current_user_or_api_key(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(reusable_oauth2_optional),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> User:
    """
    Authenticate via JWT token OR X-API-Key header.
    """
    # Try JWT first
    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = payload.get("sub")
            user = db.query(User).filter(User.id == token_data).first()
            if user:
                return user
        except (JWTError, ValidationError):
            pass  # Fall through to API key check
    
    # Try API Key
    if x_api_key:
        user = get_user_from_api_key(db, x_api_key)
        if user:
            return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

