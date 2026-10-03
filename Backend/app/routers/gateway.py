# backend/app/routers/gateway.py
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.dependencies import verify_gateway_api_key
import app.models as models

router = APIRouter(prefix="/v1", tags=["Protected Microservice Sandbox Gateway"])

async def log_api_metrics_async(endpoint: str, method: str, status_code: int, response_time_ms: float, project_id: int, key_id: int):
    async with AsyncSessionLocal() as db:
        # ✅ Enforce a safe minimum tracking limit so local loops never flatline to 0.0
        calculated_duration = max(float(response_time_ms), 0.1)
        log = models.ApiLog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=calculated_duration,
            project_id=project_id,
            key_id=key_id
        )
        db.add(log)
        await db.commit()

def enforce_scope_clearance(api_key: models.ApiKey, required_scope: str):
    allowed = [s.strip() for s in api_key.scopes.split(",")]
    if required_scope not in allowed:
        raise HTTPException(status_code=403, detail=f"Forbidden access: Missing mandatory '{required_scope}' scope permission context.")

@router.get("/products")
async def read_products(background_tasks: BackgroundTasks, api_key: models.ApiKey = Depends(verify_gateway_api_key)):
    start = time.perf_counter()
    enforce_scope_clearance(api_key, "read")
    # ✅ Multiplied by 1000 to convert clean fractional values directly into full millisecond scales
    duration = (time.perf_counter() - start) * 1000.0
    
    background_tasks.add_task(log_api_metrics_async, "/api/v1/products", "GET", 200, duration, api_key.project_id, api_key.id)
    return {"products": ["Core Processor", "Memory Grid Core Container Component", "Solid State Drive Platform Array"]}

@router.post("/products")
async def write_products(background_tasks: BackgroundTasks, api_key: models.ApiKey = Depends(verify_gateway_api_key)):
    start = time.perf_counter()
    enforce_scope_clearance(api_key, "write")
    duration = (time.perf_counter() - start) * 1000.0
    
    background_tasks.add_task(log_api_metrics_async, "/api/v1/products", "POST", 201, duration, api_key.project_id, api_key.id)
    return {"message": "Product created successfully inside secure datastore nodes."}

@router.delete("/products/{id}")
async def erase_product(id: int, background_tasks: BackgroundTasks, api_key: models.ApiKey = Depends(verify_gateway_api_key)):
    start = time.perf_counter()
    enforce_scope_clearance(api_key, "delete")
    duration = (time.perf_counter() - start) * 1000.0
    
    background_tasks.add_task(log_api_metrics_async, f"/api/v1/products/{id}", "DELETE", 200, duration, api_key.project_id, api_key.id)
    return {"message": f"Product instance data node identification reference #{id} deleted."}
