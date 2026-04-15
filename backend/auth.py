from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid
from datetime import datetime, timedelta
import hashlib

users = []

router = APIRouter(prefix="/auth", tags=["Auth"])

# Keep bcrypt only for verifying old hashes if any exist.
# New passwords will use pbkdf2_sha256, which avoids the bcrypt 72-byte issue.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class RegisterRequest(BaseModel):
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    password: str
    confirm_password: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def normalize_password(password: str) -> str:
    """
    Pre-hash the raw password so long passwords are handled safely and consistently.
    This avoids bcrypt's 72-byte limit and works fine with pbkdf2_sha256 too.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    normalized = normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized = normalize_password(plain_password)
    return pwd_context.verify(normalized, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
def register(request: RegisterRequest):
    existing_user = next((u for u in users if u["email"].lower() == request.email.lower()), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not request.password or len(request.password.strip()) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    if request.confirm_password is not None and request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    new_user = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "email": request.email.lower(),
        "phone": request.phone,
        "password": hash_password(request.password),
        "created_at": datetime.utcnow().isoformat()
    }

    users.append(new_user)

    access_token = create_access_token({"sub": new_user["id"]})

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "phone": new_user["phone"]
        }
    }


@router.post("/login")
def login(request: LoginRequest):
    user = next((u for u in users if u["email"].lower() == request.email.lower()), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user["id"]})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user.get("name"),
            "email": user["email"],
            "phone": user.get("phone")
        }
    }


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user.get("name"),
        "email": current_user["email"],
        "phone": current_user.get("phone")
    }
