# backend/app/main.py
import secrets
import time
from fastapi import FastAPI, Depends, HTTPException, status, Path, Query, Header, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List, Optional

from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas
from app.security import hash_password, verify_password, create_access_token

app = FastAPI(title="KeyShield Dev Engine", version="0.8.0")

# 1. GLOBAL MIDDLEWARE: CORS POLICY ENGINE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. GLOBAL MIDDLEWARE: CUSTOM PERFORMANCE PROFILING TIME INTERCEPTOR
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Intercept: Start clock before routing hits endpoint
    start_time = time.perf_counter()
    
    # Process the request down the pipeline
    response = await call_next(request)
    
    # Intercept: Stop clock after endpoint logic resolves
    process_time = time.perf_counter() - start_time
    
    # Convert execution duration to milliseconds string format
    execution_ms = f"{process_time * 1000:.2f}ms"
    
    # Inject custom performance headers into the network response packet
    response.headers["X-Process-Time"] = execution_ms
    print(f"[PERF-LOG] Network Route: {request.url.path} | Execution Duration: {execution_ms}")
    
    return response


# --- BACKGROUND WORKER TASK SIMULATOR ---
def log_key_activity_worker(key_name: str, key_owner_id: int):
    """Simulates a heavy logging operation that executes after the response is sent."""
    print(f"\n[BACKGROUND WORKER START] Processing audit logs for key: '{key_name}'...")
    # Simulating a small database write delay or processing lag
    time.sleep(1.5)
    print(f"[BACKGROUND WORKER SUCCESS] Audit entry saved to disk for User #{key_owner_id}.\n")


# --- DEVELOPER CLIENT AUTH DEPENDENCY GUARD (From Day 7) ---
async def verify_developer_api_key(x_api_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="X-API-Key header missing.")
    stmt = select(models.ApiKey).where(models.ApiKey.key_value == x_api_key)
    result = await db.execute(stmt)
    db_key = result.scalars().first()
    if not db_key or not db_key.is_active:
        raise HTTPException(status_code=403, detail="Invalid or deactivated API Key.")
    return db_key


# --- SYSTEM LOG INGESTION ENDPOINTS ---

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "KeyShield API is running"}

@app.post("/api/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="An account with this email is already registered.")

    secured_hash = hash_password(user_data.password)
    new_user = models.User(email=user_data.email, hashed_password=secured_hash)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/api/login", response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(models.User).where(models.User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/users/{user_id}/keys", response_model=schemas.KeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key(key_data: schemas.KeyCreate, user_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    user_query = select(models.User).where(models.User.id == user_id)
    user_result = await db.execute(user_query)
    if not user_result.scalars().first():
        raise HTTPException(status_code=404, detail="User does not exist.")
    secure_token = f"ks_{secrets.token_hex(24)}"
    new_key = models.ApiKey(key_value=secure_token, name=key_data.name, user_id=user_id)
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return new_key

@app.get("/api/users/{user_id}/keys", response_model=List[schemas.KeyResponse])
async def get_user_keys(user_id: int, active_only: Optional[bool] = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(models.ApiKey).where(models.ApiKey.user_id == user_id)
    if active_only is not None:
        stmt = stmt.where(models.ApiKey.is_active == active_only)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.patch("/api/keys/{key_id}/deactivate", response_model=schemas.KeyResponse)
async def deactivate_key(key_id: int, db: AsyncSession = Depends(get_db)):
    key_query = select(models.ApiKey).where(models.ApiKey.id == key_id)
    key_result = await db.execute(key_query)
    db_key = key_result.scalars().first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found.")
    db_key.is_active = False
    await db.commit()
    await db.refresh(db_key)
    return db_key


# --- REVISED AUTHENTICATED RESOURCE ROUTE: NOW WITH BACKGROUND LOGGING ---
@app.get("/api/v1/secure-data")
async def get_secure_resource(
    background_tasks: BackgroundTasks,
    authenticated_key: models.ApiKey = Depends(verify_developer_api_key)
):
    """Locked data grid pathway. Registers a background tracking step upon entry validation verification."""
    
    # 1. Enqueue the slow logging execution task to the background pool thread manager
    background_tasks.add_task(
        log_key_activity_worker, 
        key_name=authenticated_key.name, 
        key_owner_id=authenticated_key.user_id
    )
    
    # 2. Return an immediate, fast response back to the client while the task processes quietly
    return {
        "status": "Authorized Access Grant Verified",
        "secret_payload": "This data pipeline is protected and monitored by background metrics handlers.",
        "key_owner_id": authenticated_key.user_id
    }
