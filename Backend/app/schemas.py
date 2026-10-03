from pydantic import BaseModel, EmailStr, Field
import datetime
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2)
    rate_limit_rpm: Optional[int] = 60

class ProjectResponse(BaseModel):
    id: int
    name: str
    rate_limit_rpm: int
    user_id: int
    class Config:
        from_attributes = True

class KeyCreate(BaseModel):
    name: str
    environment: str = Field(..., description="Development, Staging, Production")
    scopes: List[str] = Field(default=["read"])

class KeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    environment: str
    scopes: str
    is_active: bool
    created_at: datetime.datetime
    project_id: int
    class Config:
        from_attributes = True

class KeyDisplay(KeyResponse):
    raw_key: Optional[str] = None # Filled ONLY on raw creation return mutation

class AnalyticsSummary(BaseModel):
    total_requests: int
    success_count: int
    failed_count: int
    avg_response_time_ms: float

class LogResponse(BaseModel):
    id: int
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime.datetime
    class Config:
        from_attributes = True
