# backend/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import engine, Base, get_db
import app.models as models

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
