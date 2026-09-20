# backend/app/main.py
import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List

from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas

app = FastAPI(title="KeyShield Dev Engine", version="0.3.0")

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

# --- USER SIGNUP ENDPOINT ---
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

# --- NEW ROUTE: DYNAMIC API KEY GENERATION ENDPOINT ---
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User account with ID {user_id} does not exist."
        )

    secure_token = f"ks_{secrets.token_hex(24)}"

    new_key = models.ApiKey(
        key_value=secure_token,
        name=key_data.name,
        user_id=user_id
    )

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return new_key
