from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.database import engine, Base, get_db
import app.models as models
import app.schemas as schemas

app = FastAPI(
    title="KeyShield Dev Engine",
    description="Foundational backend service managing application access metrics.",
    version="0.1.0"
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

@app.post("/api/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(models.User).where(models.User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email is already registered."
        )

    new_user = models.User(
        email=user_data.email,
        hashed_password=user_data.password 
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
