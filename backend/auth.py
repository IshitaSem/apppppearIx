from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from datetime import datetime, timedelta
from database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b9tnv9b929c09774b2e2b"  # Change in production
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


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user["id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
def register(request: RegisterRequest):
    if db.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = {
        "id": str(uuid.uuid4()),
        "email": request.email.lower(),
        "password": hash_password(request.password),
        "created_at": datetime.utcnow().isoformat()
    }

    if not db.create_user(new_user):
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user_id": new_user["id"],
            "email": new_user["email"]
        }
    }


@router.post("/login")
def login(request: LoginRequest):
    user = db.get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": user["id"]})

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "email": user["email"]
        }
    }


@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):
    user = db.get_user_by_id(user_id)
    if user:
        return {
            "user_id": user["id"],
            "email": user["email"]
        }
    raise HTTPException(status_code=404, detail="User not found")

