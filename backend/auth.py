from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import uuid
import os

from database import users_collection, serialize_doc

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
def register(request: RegisterRequest):
    email = request.email.strip().lower()
    password = request.password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        hashed_password = hash_password(password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password hashing failed: {str(e)}")

    new_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        users_collection.insert_one(new_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user_id": new_user["id"],
            "email": new_user["email"],
        },
    }


@router.post("/login")
def login(request: LoginRequest):
    email = request.email.strip().lower()
    password = request.password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    try:
        if not verify_password(password, user["password"]):
            raise HTTPException(status_code=400, detail="Wrong password")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password verification failed: {str(e)}")

    token = create_access_token({"sub": user["id"]})

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "email": user["email"],
        },
    }


@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = serialize_doc(user)

    return {
        "user_id": user["id"],
        "email": user["email"],
    }
