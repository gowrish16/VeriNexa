import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
import psycopg2
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "verilit-super-secret-key-biomedical-audit-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, COALESCE(hashed_password, password_hash), full_name, created_at FROM users WHERE LOWER(email) = LOWER(%s);",
        (email.strip(),)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "full_name": row[3],
            "created_at": row[4]
        }
    return None


def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, COALESCE(hashed_password, password_hash), full_name, created_at FROM users WHERE id = %s;",
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "full_name": row[3],
            "created_at": row[4]
        }
    return None


async def get_current_user(
    token_bearer: Optional[str] = Depends(oauth2_scheme),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
) -> dict:
    token = token_bearer or (credentials.credentials if credentials else None)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_optional_user(
    token_bearer: Optional[str] = Depends(oauth2_scheme),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
) -> Optional[dict]:
    token = token_bearer or (credentials.credentials if credentials else None)
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            return None
        return get_user_by_id(int(user_id_str))
    except Exception:
        return None


# ---------------- Schemas ----------------
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------- Endpoints ----------------
@router.post("/register")
def register(req: RegisterRequest):
    clean_email = req.email.strip().lower()
    if not clean_email or not req.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    existing_user = get_user_by_email(clean_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed = hash_password(req.password)
    clean_name = (req.full_name or "").strip() or clean_email.split("@")[0]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (email, hashed_password, password_hash, full_name)
        VALUES (%s, %s, %s, %s)
        RETURNING id, created_at;
        """,
        (clean_email, hashed, hashed, clean_name)
    )
    new_user_id, created_at = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    token = create_access_token({"sub": str(new_user_id), "email": clean_email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user_id,
            "email": clean_email,
            "full_name": clean_name,
            "created_at": str(created_at)
        }
    }


@router.post("/login")
async def login(request: Request):
    content_type = request.headers.get("content-type", "")
    email = None
    password = None

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = (form.get("username") or form.get("email") or "").strip().lower()
        password = form.get("password")
    else:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = (body.get("email") or body.get("username") or "").strip().lower()
                password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": str(user["created_at"])
        }
    }


@router.get("/me")
def get_current_user_profile(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "created_at": str(user["created_at"])
    }
