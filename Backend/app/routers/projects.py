# backend/app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_user
import app.models as models
import app.schemas as schemas
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects Context Module"])

@router.post("", response_model=schemas.ProjectResponse, status_code=201)
async def create_project(proj_in: schemas.ProjectCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = models.Project(name=proj_in.name, rate_limit_rpm=proj_in.rate_limit_rpm, user_id=current_user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.get("", response_model=List[schemas.ProjectResponse])
async def list_projects(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(models.Project).where(models.Project.user_id == current_user.id))
    return res.scalars().all()

@router.get("/{project_id}/analytics", response_model=schemas.AnalyticsSummary)
async def get_project_analytics(project_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    p_res = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    if not p_res.scalars().first():
        raise HTTPException(status_code=404, detail="Project context target missing.")
    
    total = await db.execute(select(func.count(models.ApiLog.id)).where(models.ApiLog.project_id == project_id))
    success = await db.execute(select(func.count(models.ApiLog.id)).where(models.ApiLog.project_id == project_id, models.ApiLog.status_code < 400))
    failed = await db.execute(select(func.count(models.ApiLog.id)).where(models.ApiLog.project_id == project_id, models.ApiLog.status_code >= 400))
    avg_time = await db.execute(select(func.coalesce(func.avg(models.ApiLog.response_time_ms), 0.0)).where(models.ApiLog.project_id == project_id))
    
    return {
        "total_requests": total.scalar() or 0,
        "success_count": success.scalar() or 0,
        "failed_count": failed.scalar() or 0,
        "avg_response_time_ms": round(float(avg_time.scalar() or 0.0), 2)
    }


@router.get("/{project_id}/logs", response_model=List[schemas.LogResponse])
async def get_project_logs(project_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    p_res = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    if not p_res.scalars().first():
        raise HTTPException(status_code=404, detail="Project log array reference error.")
    res = await db.execute(select(models.ApiLog).where(models.ApiLog.project_id == project_id).order_by(models.ApiLog.timestamp.desc()).limit(50))
    return res.scalars().all()
