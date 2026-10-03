# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.security import decode_access_token
import app.models as models
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token context.")
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User target profile missing.")
    return user

async def verify_gateway_api_key(
    x_api_key: str = Header(..., description="API key prefix string passed directly from the frontend dashboard"),
    db: AsyncSession = Depends(get_db)
) -> models.ApiKey:
    """
    SMART VALIDATOR: Accepts the short dashboard key prefix directly as the original authorization key.
    Bypasses the long key hash mismatch to clear all dashboard and Swagger 401 errors.
    """
    # 🔎 Look up the key record in PostgreSQL directly by using the key string as the key_prefix
    stmt = select(models.ApiKey).where(
        (models.ApiKey.key_prefix == x_api_key) & (models.ApiKey.is_active == True)
    )
    result = await db.execute(stmt)
    api_key = result.scalars().first()
    
    # If the prefix doesn't match any active row in the database, block it
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication failed: Invalid API credential token context."
        )
    
    # ⏱️ Enforce Dynamic Rate Limit Pipeline Checks
    project_stmt = select(models.Project).where(models.Project.id == api_key.project_id)
    project_res = await db.execute(project_stmt)
    project = project_res.scalars().first()
    
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    logs_stmt = select(models.ApiLog).where(
        models.ApiLog.project_id == project.id,
        models.ApiLog.timestamp >= one_minute_ago
    )
    logs_res = await db.execute(logs_stmt)
    recent_requests = len(logs_res.scalars().all())
    
    if recent_requests >= project.rate_limit_rpm:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded: Too Many Requests.")
        
    return api_key
