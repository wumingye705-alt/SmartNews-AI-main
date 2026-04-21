from fastapi import Header, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config import JWT_SECRET_KEY, JWT_ALGORITHM
from config.db_config import get_db
from crud import users

async def get_current_user(
        authorization: str = Header(..., alias="Authorization"),
        db: AsyncSession = Depends(get_db)
) -> users.User:
    """根据JWT token获取当前用户"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解析Authorization头部
        token = authorization.replace("Bearer", "").strip()

        # 验证JWT token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 根据用户ID获取用户
    user = await users.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user