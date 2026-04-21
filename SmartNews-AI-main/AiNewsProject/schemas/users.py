from typing import Optional

from numpy.ma.core import minimum
from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    """用户信息基础数据模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像 URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserInfo(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True # 允许从模型属性填充数据
    )


class UserVerify(BaseModel):
    token: str
    user_info: UserInfo = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True, # 允许根据字段名填充数据
        from_attributes=True # 允许从模型属性填充数据
    )


class UserInfoUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像 URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserPasswordUpdate(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")
