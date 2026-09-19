from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr 

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters.")

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
