# app/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from app.database import AsyncSessionLocal
from sqlalchemy import select
from . import models

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Получает текущего пользователя по Bearer токену
    Если токен не передан - None
    """
    if token is None:
        return None
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        # token.credentials содержит сам токен
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.User).where(models.User.username == username))
        user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
