from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from models import News
from models.history import History
from schemas.history import HistoryNewsItem
from schemas.news import NewsItemBase


async def add_news_history(
        user_id: int,
        news_id: int,
        db: AsyncSession = Depends(get_db)
) -> History | None:
    """添加新闻浏览历史"""
    # 检查是否已经有浏览历史
    existing_history = await db.execute(select(History).where(History.user_id == user_id, History.news_id == news_id))
    history = existing_history.scalar_one_or_none()
    
    if history:
        # 如果已经有浏览历史，则更新浏览时间
        history.view_time = datetime.now()
        await db.commit()
        await db.refresh(history)
        return history

    # 如果没有浏览历史，则创建一个新的浏览记录
    history = History(
        user_id=user_id,
        news_id=news_id,
        view_time=datetime.now(),
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_news_history_list(
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        db: AsyncSession = Depends(get_db)
):
    """获取用户浏览记录列表"""
    # 总量 + 收藏的新闻列表
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 收藏的新闻总数

    # 获取收藏的新闻列表 - 联表查询 + 排序 + 分页
    query = (
        select(News, History.view_time.label('view_time'))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    result = await db.execute(query)
    history_news_list = result.all()

    # 构建响应数据 - 使用 Pydantic 模型类
    news_list = []
    for news, view_time in history_news_list:
        news_item_base = NewsItemBase.model_validate(news, from_attributes=True)
        news_data_dict = news_item_base.model_dump(mode='json')
        news_data_dict["view_time"] = view_time

        # 使用 HistoryNewsItem 验证完整数据
        history_news_item = HistoryNewsItem(**news_data_dict)

        # 转换为字典并使用别名
        news_data = history_news_item.model_dump(mode='json', by_alias=True)
        news_list.append(news_data)

    has_more = (page - 1) * page_size + len(news_list) < total

    return {
        "list": news_list,
        "total": total,
        "hasMore": has_more
    }


async def remove_news_history(
        user_id: int,
        news_id: int,
        db: AsyncSession = Depends(get_db)
):
    """删除用户浏览记录"""
    # 查询指定用户和新闻的浏览记录
    result = await db.execute(
        select(History).where(History.user_id == user_id, History.news_id == news_id)
    )
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(status_code=404, detail="浏览记录不存在")

    # 删除该浏览记录
    await db.delete(history)
    await db.commit()
    
    # 返回是否删除成功
    return history is None



async def clear_news_history(
        user_id: int,
        db: AsyncSession = Depends(get_db)
) -> bool:
    """清空用户所有浏览记录"""
    # 删除该用户所有浏览记录
    await db.execute(
        delete(History).where(History.user_id == user_id)
    )
    await db.commit()

    # 返回是否清空成功
    return True
