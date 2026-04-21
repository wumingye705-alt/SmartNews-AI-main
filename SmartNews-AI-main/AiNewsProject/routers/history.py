from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from config.db_config import get_db
from crud.history import add_news_history, get_news_history_list, remove_news_history, clear_news_history
from models import User
from schemas.history import HistoryItem
from utils.auth import get_current_user
from utils.success_response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        history_item: HistoryItem,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """添加浏览记录"""
    history = await add_news_history(user.id, history_item.news_id, db)

    data = {
        "id": history.id,
        "userId": history.user_id,
        "newsId": history.news_id,
        "viewTime": history.view_time,
    }

    return success_response(message="添加成功", data=data)


@router.get("/list")
async def get_history_list(
        page: int = Query(1, alias="page", description="页码"),
        page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """获取浏览记录列表"""
    data = await get_news_history_list(user.id, page, page_size, db)

    return success_response(message="获取成功", data=data)

@router.delete("/delete/{news_id}")
async def delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
        """删除浏览记录"""
        await remove_news_history(user.id, news_id, db)

        return success_response(message="删除成功", data=None)


@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
        """清空所有浏览记录"""
        await clear_news_history(user.id, db)

        return success_response(message="清空成功", data=None)

