# backend/app/routers/keys.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user
import app.models as models
import app.schemas as schemas
from app.security import generate_key_hash
from typing import List

router = APIRouter(prefix="/projects/{project_id}/keys", tags=["API Keys System Workspace"])

@router.post("", response_model=schemas.KeyDisplay, status_code=201)
async def generate_key(project_id: int, key_in: schemas.KeyCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    p_res = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    if not p_res.scalars().first():
        raise HTTPException(status_code=404, detail="Parent project context mapping missing.")
        
    env_tag = "live" if key_in.environment.lower() == "production" else "test"
    secret_raw = f"ks_{env_tag}_{secrets.token_hex(20)}"
    prefix = secret_raw[:12]
    hashed = generate_key_hash(secret_raw)
    
    api_key = models.ApiKey(
        name=key_in.name,
        key_prefix=prefix,
        hashed_key=hashed,
        environment=key_in.environment,
        scopes=",".join(key_in.scopes),
        project_id=project_id
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    api_key.raw_key = secret_raw # Expose unhashed key exactly once to caller client
    return api_key

@router.get("", response_model=List[schemas.KeyResponse])
async def list_keys(project_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.ApiKey).join(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    return res.scalars().all()

@router.post("/{key_id}/rotate", response_model=schemas.KeyDisplay)
async def rotate_key(project_id: int, key_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.ApiKey).join(models.Project).where(
        models.ApiKey.id == key_id,
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    )
    res = await db.execute(stmt)
    old_key = res.scalars().first()
    if not old_key:
        raise HTTPException(status_code=404, detail="API Key structural identifier invalid.")
        
    env_tag = "live" if old_key.environment.lower() == "production" else "test"
    secret_raw = f"ks_{env_tag}_{secrets.token_hex(20)}"
    
    old_key.key_prefix = secret_raw[:12]
    old_key.hashed_key = generate_key_hash(secret_raw)
    old_key.is_active = True
    
    await db.commit()
    await db.refresh(old_key)
    old_key.raw_key = secret_raw
    return old_key

@router.patch("/{key_id}/deactivate", response_model=schemas.KeyResponse)
async def deactivate_key(project_id: int, key_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.ApiKey).join(models.Project).where(
        models.ApiKey.id == key_id,
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    )
    res = await db.execute(stmt)
    api_key = res.scalars().first()
    if not api_key:
        raise HTTPException(status_code=404, detail="Key modification query invalid.")
    api_key.is_active = False
    await db.commit()
    return api_key
