import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Path, Query, Header
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

app = FastAPI(title="KeyShield Dev Engine", version="0.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "KeyShield API is running"}

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

# --- REVISED USER SIGNUP ENDPOINT: NOW WITH PASSWORD HASHING ---
@app.post("/api/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="An account with this email is already registered.")

    # Convert raw text password into an encrypted cryptographic hash
    secured_hash = hash_password(user_data.password)

    new_user = models.User(email=user_data.email, hashed_password=secured_hash)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# --- NEW ROUTE: WEB LOGIN ENDPOINT (ISSUES SIGNED JWT ACCESS TOKENS) ---
@app.post("/api/login", response_model=schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # Find user matching incoming username form field parameter entry
    query = select(models.User).where(models.User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    # Reject authorization request if user record missing or hash verification fails
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue a signed JWT tracking user identity parameters
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- OTHER CORE APP MANAGEMENT ROUTE LIFECYCLES ---

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

@app.get("/api/v1/secure-data")
async def get_secure_resource(authenticated_key: models.ApiKey = Depends(verify_developer_api_key)):
    return {
        "status": "Authorized Access Grant Verified",
        "secret_payload": "This data payload belongs strictly to authenticated corporate client systems.",
        "key_owner_id": authenticated_key.user_id
    }
