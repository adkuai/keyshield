from datetime import datetime, timedelta
from typing import Optional
from pwdlib import PasswordHash
import jwt

# Instantiate the modern secure cryptographic hashing manager
password_hash = PasswordHash.recommended()

SECRET_KEY = "LOCAL_DEVELOPMENT_ONLY_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    """Transforms a plain text password into an unreadable secure cryptographic hash."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares incoming plain text login entry against the encrypted hash string."""
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an encrypted JSON Web Token (JWT) tracking session identification data."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
