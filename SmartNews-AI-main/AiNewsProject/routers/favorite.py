from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.favorite import is_news_favorite, add_news_favorite, remove_news_favorite, get_news_favorite_list, \
    clear_news_favorite
from models.user import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteAddResponse
from utils.auth import get_current_user
from utils.success_response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """检查是否收藏"""
    is_favorite = await is_news_favorite(user.id, news_id, db)
    result = FavoriteCheckResponse(isFavorite=is_favorite)

    return success_response(
        message="检查收藏成功",
        data=result
    )


@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """添加收藏"""
    favorite = await add_news_favorite(user.id, data.news_id, db)
    result = FavoriteAddResponse.from_orm(favorite)

    return success_response(
        message="添加收藏成功",
        data=result
    )


@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """删除收藏"""

    data = await remove_news_favorite(user.id, news_id, db)

    return success_response(
        message="删除收藏成功",
        data=data
    )

@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, alias="page", ge=1, description="页码"),
        page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """获取收藏列表"""

    data = await get_news_favorite_list(user.id, page, page_size, db)

    return success_response(
        message="获取收藏列表成功",
        data=data
    )


@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """清空收藏"""

    data = await clear_news_favorite(user.id, db)

    return success_response(message=f"成功删除{data}条收藏", data=None)
