from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import auth

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str = ""
    token: str = ""
    username: str = ""


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    result = auth.login_user(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return AuthResponse(
        success=True,
        token=result["token"],
        username=result["username"],
    )


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少3个字符")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6个字符")
    result = auth.register_user(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return AuthResponse(
        success=True,
        token=result["token"],
        username=result["username"],
    )


@router.get("/me")
async def get_current_user(token: str = ""):
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    username = auth.decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    return {"username": username}
