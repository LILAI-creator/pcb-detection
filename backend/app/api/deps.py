from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services import auth

security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    username = auth.decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    user_id = auth.get_user_id_by_username(username)
    if not user_id:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user_id
