from datetime import datetime, timedelta
from typing import Dict, Any

from jose import jwt

from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES


class TokenService:
    """Token服务类，处理token的生成、验证和管理"""

    async def create_token(self, user_id: int) -> str:
        """
        创建JWT令牌
        :param user_id: 用户ID
        :return: JWT令牌
        """
        # 创建JWT payload
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "exp": expire
        }

        # 生成JWT令牌
        access_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return access_token