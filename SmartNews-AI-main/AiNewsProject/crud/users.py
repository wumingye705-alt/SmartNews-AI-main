import os
import shutil
import time

from fastapi import HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependence.generate_token import TokenService
from models.user import User
from schemas.users import UserRequest, UserInfoUpdate, UserPasswordUpdate
from utils.secure import get_password_hash, verify_password


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    """
    根据用户名查询用户
    :param db: 数据库会话
    :param username: 用户名
    :return: 用户对象或None
    """
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """
    根据用户ID查询用户
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 用户对象或None
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRequest) -> User:
    """
    创建用户，密码使用passlib加密，其他字段直接从user_data中获取
    :param db: 数据库会话
    :param user_data: 用户请求数据
    :return: 创建的用户对象
    """
    # 密码加密
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        password = hashed_password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user) # 从数据库重新加载用户信息，确保返回的用户对象是最新的
    return user


async def get_token_service() -> TokenService:
    """获取Token服务实例 - 不再需要数据库依赖"""
    return TokenService()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User|None:
    """
    验证用户身份
    :param db: 数据库会话
    :param username: 用户名
    :param password: 密码
    :return: 如果验证成功则返回用户对象，否则返回None
    """
    user = await get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


async def update_user_information(db: AsyncSession, user: User, user_update: UserInfoUpdate) -> User:
    """
    更新用户信息
    :param db: 数据库会话
    :param user: 要更新的用户对象
    :param user_update: 用户更新数据
    :return: 更新后的用户对象
    """
    update_data = user_update.model_dump(exclude_unset=True)

    # 更新用户信息
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(db: AsyncSession, user: User, password_update: UserPasswordUpdate) -> User:
    """
    更新用户密码
    :param db: 数据库会话
    :param user: 要更新密码的用户对象
    :param password_update: 密码更新数据
    :return: 更新后的用户对象
    """
    # 验证旧密码
    if not verify_password(password_update.old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 更新密码
    user.password = get_password_hash(password_update.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def upload_avatar(
        db: AsyncSession,
        user: User,
        avatar_file: UploadFile = File(...)
):
    """上传用户头像, 用户上传头像图片文件之后，将图片保存到avatar目录，然后数据库里存储头像图片的文件名"""
    # 检查文件类型
    if not avatar_file.filename.endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="仅支持jpg, jpeg, png格式的图片")

    # 检查文件大小（限制为5MB）
    if avatar_file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

    # 确保avatar目录存在
    os.makedirs("avatar", exist_ok=True)

    # 生成唯一的文件名
    filename = f"{user.id}_{int(time.time())}_{avatar_file.filename}"
    file_path = os.path.join("avatar", filename)

    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar_file.file, buffer)
    finally:
        await avatar_file.close()

    # 只存储文件名，而不是完整路径！
    user.avatar = filename
    await db.commit()
    await db.refresh(user)

    return user