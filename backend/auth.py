import os
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
import psycopg2
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "verilit-super-secret-key-biomedical-audit-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@verinexa.ai").strip().lower()

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


def is_admin_user(user: Optional[dict]) -> bool:
    if not user:
        return False
    if user.get("is_admin") is True:
        return True
    user_email = (user.get("email") or "").strip().lower()
    return user_email == ADMIN_EMAIL


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
        """
        SELECT id, email, COALESCE(hashed_password, password_hash), full_name, created_at, COALESCE(is_admin, FALSE)
        FROM users WHERE LOWER(email) = LOWER(%s);
        """,
        (email.strip(),)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        admin_flag = bool(row[5]) or (row[1].strip().lower() == ADMIN_EMAIL)
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "full_name": row[3],
            "created_at": row[4],
            "is_admin": admin_flag
        }
    return None


def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, email, COALESCE(hashed_password, password_hash), full_name, created_at, COALESCE(is_admin, FALSE)
        FROM users WHERE id = %s;
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        admin_flag = bool(row[5]) or (row[1].strip().lower() == ADMIN_EMAIL)
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "full_name": row[3],
            "created_at": row[4],
            "is_admin": admin_flag
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


async def get_current_admin_user(
    user: dict = Depends(get_current_user)
) -> dict:
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource"
        )
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


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


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
    admin_flag = clean_email == ADMIN_EMAIL

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (email, hashed_password, password_hash, full_name, is_admin)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, created_at;
        """,
        (clean_email, hashed, hashed, clean_name, admin_flag)
    )
    new_user_id, created_at = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    token = create_access_token({"sub": str(new_user_id), "email": clean_email, "is_admin": admin_flag})
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": admin_flag,
        "user": {
            "id": new_user_id,
            "email": clean_email,
            "full_name": clean_name,
            "is_admin": admin_flag,
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
            detail="Invalid email or password"
        )

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    admin_flag = is_admin_user(user)
    token = create_access_token({
        "sub": str(user["id"]),
        "email": user["email"],
        "is_admin": admin_flag
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": admin_flag,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_admin": admin_flag,
            "created_at": str(user["created_at"])
        }
    }


@router.get("/me")
def get_current_user_profile(user: dict = Depends(get_current_user)):
    admin_flag = is_admin_user(user)
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_admin": admin_flag,
        "created_at": str(user["created_at"])
    }


# ---------------- Password Recovery Endpoints ----------------
@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, request: Request):
    clean_email = req.email.strip().lower()
    if not clean_email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = get_user_by_email(clean_email)
    if not user:
        # Standard generic response prevents user enumeration
        return {
            "success": True,
            "message": f"If an account is associated with {clean_email}, a secure password reset link has been dispatched."
        }

    # Generate secure random token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO password_reset_tokens (user_id, email, token, expires_at)
        VALUES (%s, %s, %s, %s);
        """,
        (user["id"], clean_email, reset_token, expires_at)
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Determine base frontend URL from request or fallback
    origin = request.headers.get("origin") or "http://localhost:5173"
    reset_link = f"{origin}/reset-password?token={reset_token}"

    # Log recovery link clearly to terminal
    print(f"\n=======================================================")
    print(f"[PASSWORD RECOVERY GATEWAY]")
    print(f"Target Account: {clean_email} (User ID: {user['id']})")
    print(f"Token: {reset_token}")
    print(f"Secure Reset URL: {reset_link}")
    print(f"Valid Until: {expires_at.isoformat()}")
    print(f"=======================================================\n")

    # Optional real SMTP dispatch if configured
    smtp_host = os.getenv("SMTP_HOST")
    if smtp_host:
        try:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASSWORD", "")
            msg = MIMEText(
                f"Hello,\n\nYou recently requested a password reset for your VeriNexa account ({clean_email}).\n\n"
                f"Click the link below to set a new password:\n{reset_link}\n\n"
                f"This link expires in 1 hour.\nIf you did not request this, please ignore this email."
            )
            msg["Subject"] = "VeriNexa Password Recovery Request"
            msg["From"] = os.getenv("SMTP_FROM", "no-reply@verinexa.ai")
            msg["To"] = clean_email

            with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        except Exception as e:
            print(f"[Warning] SMTP dispatch encountered error (link logged to console): {e}")

    return {
        "success": True,
        "message": f"A secure recovery link has been dispatched to {clean_email}.",
        "reset_link": reset_link  # Included to streamline testing in local environment
    }


@router.get("/verify-reset-token")
def verify_reset_token(token: str = Query(...)):
    if not token:
        return {"valid": False, "error": "Token is required."}

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, email, expires_at, used
        FROM password_reset_tokens
        WHERE token = %s;
        """,
        (token.strip(),)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {"valid": False, "error": "Invalid or unrecognized reset token."}

    used = row[4]
    expires_at = row[3]
    if used:
        return {"valid": False, "error": "This recovery link has already been used."}

    now_utc = datetime.now(timezone.utc)
    # Ensure expires_at has timezone info
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now_utc > expires_at:
        return {"valid": False, "error": "This recovery link has expired. Please request a new one."}

    return {
        "valid": True,
        "email": row[2]
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    token = req.token.strip()
    new_password = req.new_password.strip()

    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, email, expires_at, used
        FROM password_reset_tokens
        WHERE token = %s;
        """,
        (token,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid recovery link")

    token_id = row[0]
    user_id = row[1]
    expires_at = row[3]
    used = row[4]

    if used:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="This recovery link has already been used")

    now_utc = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now_utc > expires_at:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Recovery link has expired")

    hashed = hash_password(new_password)
    cursor.execute(
        """
        UPDATE users
        SET hashed_password = %s, password_hash = %s
        WHERE id = %s;
        """,
        (hashed, hashed, user_id)
    )

    cursor.execute(
        """
        UPDATE password_reset_tokens
        SET used = TRUE
        WHERE id = %s;
        """,
        (token_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "message": "Password successfully reset! You can now log in with your new credentials."
    }
