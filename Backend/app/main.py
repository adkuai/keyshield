import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, projects, keys, gateway

app = FastAPI(title="KeyShield Core Enterprise API Engine", version="1.0.0")

# FORCE EXPLICIT CORS POLICY GRANTS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Clear your local dev ports explicitly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def performance_profiler_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start_time) * 1000
    response.headers["X-Response-Time-Ms"] = f"{duration:.2f}ms"
    return response

@app.on_event("startup")
async def startup_initialization():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(keys.router, prefix="/api")
app.include_router(gateway.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "KeyShield Gateway Ingestion Engine Online"}
