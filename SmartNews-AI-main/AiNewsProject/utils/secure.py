from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """密码校验"""
    return pwd_context.verify(plain_password, hashed_password)