import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/api/auth")

SECRET_KEY = "medicine-ai-system-jwt-secret-key-2024"
USERS = {
    "admin": {"password": "admin123", "nickname": "管理员", "avatar": "", "roles": ["admin"]},
}


def _base64url_encode(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode()


def _base64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return urlsafe_b64decode(data)


def create_token(username: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"username": username, "iat": int(time.time()), "exp": int(time.time()) + 86400}
    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def verify_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
        actual_sig = _base64url_decode(signature_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_base64url_decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


@router.post("/login")
async def login(request: Request):
    body = await request.json()
    username = body.get("username", "")
    password = body.get("password", "")

    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_token(username)
    refresh_token = create_token(username)

    return {
        "code": 200,
        "message": "登录成功",
        "timestamp": int(time.time() * 1000),
        "data": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "username": username,
                "nickname": user["nickname"],
                "avatar": user["avatar"],
                "roles": user["roles"],
            },
        },
    }


@router.get("/currentUser")
async def current_user(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期")

    username = payload.get("username", "")
    user = USERS.get(username, {})
    return {
        "code": 200,
        "message": "ok",
        "timestamp": int(time.time() * 1000),
        "data": {
            "username": username,
            "nickname": user.get("nickname", ""),
            "avatar": user.get("avatar", ""),
            "roles": user.get("roles", []),
        },
    }