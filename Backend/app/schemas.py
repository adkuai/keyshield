from pydantic import BaseModel, EmailStr, Field
import datetime  # Changed to standard module import

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters.")

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class KeyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Give your developer token a recognizable name.")

class KeyResponse(BaseModel):
    id: int
    key_value: str
    name: str
    is_active: bool
    created_at: datetime.datetime  # Resolves cleanly now
    user_id: int

    class Config:
        from_attributes = True
