# backend/app/main.py
import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Path, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List, Optional

from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas

app = FastAPI(title="KeyShield Dev Engine", version="0.6.0")

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
    print("[DB-LOG] Database structures synchronized perfectly.")

@app.get("/")
def read_root():
    return {"message": "KeyShield API is running"}

@app.get("/api/db-test")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "Database online", "checkpoint": result.scalar()}
    except Exception as e:
        return {"status": "Database connection offline", "error": str(e)}

# --- ADVANCED SECURITY AUTHENTICATION DEPENDENCY GUARD ---
async def verify_developer_api_key(
    x_api_key: Optional[str] = Header(None, description="The custom developer token generated via dashboard"),
    db: AsyncSession = Depends(get_db)
):
    """Intercepts request headers, parses the X-API-Key token value, and checks permissions."""
    # 1. Reject instantly if the header key is completely missing from the request packet
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication failed: X-API-Key header configuration missing."
        )

    # 2. Asynchronously query PostgreSQL to locate a row matching the provided string token token
    stmt = select(models.ApiKey).where(models.ApiKey.key_value == x_api_key)
    result = await db.execute(stmt)
    db_key = result.scalars().first()

    # 3. Deny access if the key string value does not match any entry in our system records
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication failed: Invalid Developer API Key."
        )

    # 4. Deny access if the key exists but its status column has been set to inactive
    if not db_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication failed: This API Key has been explicitly deactivated."
        )

    # 5. Success: Return the key record data so downstream routes can utilize it if necessary
    return db_key


# --- SYSTEM LOG INGESTION ENDPOINTS ---

@app.post("/api/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="An account with this email is already registered.")

    new_user = models.User(email=user_data.email, hashed_password=user_data.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/api/users/{user_id}/keys", response_model=schemas.KeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key(
    key_data: schemas.KeyCreate,
    user_id: int = Path(..., description="The ID of the developer creating this key", gt=0),
    db: AsyncSession = Depends(get_db)
):
    user_query = select(models.User).where(models.User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User account with ID {user_id} does not exist.")

    secure_token = f"ks_{secrets.token_hex(24)}"
    new_key = models.ApiKey(key_value=secure_token, name=key_data.name, user_id=user_id)

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return new_key

@app.get("/api/users/{user_id}/keys", response_model=List[schemas.KeyResponse], status_code=status.HTTP_200_OK)
async def get_user_keys(
    user_id: int = Path(..., description="The ID of the user whose keys you want to fetch", gt=0),
    active_only: Optional[bool] = Query(None, description="Optional parameter to filter keys by active status"),
    db: AsyncSession = Depends(get_db)
):
    user_query = select(models.User).where(models.User.id == user_id)
    user_result = await db.execute(user_query)
    if not user_result.scalars().first():
        raise HTTPException(status_code=404, detail=f"User account with ID {user_id} does not exist.")

    stmt = select(models.ApiKey).where(models.ApiKey.user_id == user_id)
    if active_only is not None:
        stmt = stmt.where(models.ApiKey.is_active == active_only)

    result = await db.execute(stmt)
    return result.scalars().all()

@app.patch("/api/keys/{key_id}/deactivate", response_model=schemas.KeyResponse, status_code=status.HTTP_200_OK)
async def deactivate_key(
    key_id: int = Path(..., description="The unique ID of the API key to deactivate", gt=0),
    db: AsyncSession = Depends(get_db)
):
    key_query = select(models.ApiKey).where(models.ApiKey.id == key_id)
    key_result = await db.execute(key_query)
    db_key = key_result.scalars().first()

    if not db_key:
        raise HTTPException(status_code=404, detail=f"API Key with ID {key_id} not found.")

    db_key.is_active = False
    await db.commit()
    await db.refresh(db_key)
    return db_key


# --- NEW PROTECTED TESTING ROUTE: FORWARD CLUSTER DATA PIPELINE ---
@app.get("/api/v1/secure-data", status_code=status.HTTP_200_OK)
async def get_secure_resource(
    authenticated_key: models.ApiKey = Depends(verify_developer_api_key)
):
    """This route is locked. It requires a valid, active X-API-Key header to run."""
    return {
        "status": "Authorized Access Grant Verified",
        "secret_payload": "This payload is protected data visible only to valid API callers.",
        "key_owner_id": authenticated_key.user_id,
        "key_identifier_used": authenticated_key.name
    }
