from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.users import get_user_by_username, create_user, get_token_service, authenticate_user, update_user_information, \
    update_password, upload_avatar
from dependence.generate_token import TokenService
from schemas.users import UserRequest, UserVerify, UserInfo, UserInfoUpdate, UserPasswordUpdate
from utils.auth import get_current_user
from utils.success_response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_db),
        token_service: TokenService = Depends(get_token_service)
) -> JSONResponse:
    """用户注册"""

    # 先确认用户名是否存在
    is_exist_user = await get_user_by_username(db, user_data.username)
    if is_exist_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    # 创建用户
    user = await create_user(db, user_data)
    # 使用依赖注入的token服务生成令牌
    token = await token_service.create_token(user.id)

    user_info = UserInfo.model_validate(user)

    response_data = UserVerify(
        token=token,
        userInfo=user_info
    )

    return success_response(
        message="注册成功",
        data=response_data
    )


@router.post("/login")
async def login(
        user_request: UserRequest,
        db: AsyncSession = Depends(get_db),
        token_service: TokenService = Depends(get_token_service)
) -> JSONResponse:
    """用户登录"""

    user = await authenticate_user(db, user_request.username, user_request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = await token_service.create_token(user.id)
    user_info = UserInfo.model_validate(user)
    response_data = UserVerify(
        token=token,
        userInfo=user_info
    )

    return success_response(
        message="登录成功",
        data=response_data
    )


@router.get("/info")
async def get_user_info(current_user = Depends(get_current_user)) -> JSONResponse:
    """获取用户信息"""

    user_info = UserInfo.model_validate(current_user)

    return success_response(
        message="获取用户信息成功",
        data=user_info
    )


@router.put("/update")
async def update_user_info(
        user_update: UserInfoUpdate,
        current_user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """更新用户信息"""
    # 更新用户信息
    await update_user_information(db, current_user, user_update)
    # 返回更新后的用户信息
    user_info = UserInfo.model_validate(current_user)
    return success_response(
        message="更新用户信息成功",
        data=user_info
    )


@router.put("/password")
async def update_user_password(
        user_password_update: UserPasswordUpdate,
        current_user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """更新用户密码"""
    await update_password(db, current_user, user_password_update)

    return success_response(
        message="更新用户密码成功",
        data=UserInfo.model_validate(current_user)
    )


@router.post("/upload-avatar")
async def upload_user_avatar(
        avatar_file: UploadFile = File(...),
        current_user = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """上传用户头像"""
    user = await upload_avatar(db, current_user, avatar_file)
    user_info = UserInfo.model_validate(user)

    return success_response(
        message="头像上传成功",
        data=user_info
    )