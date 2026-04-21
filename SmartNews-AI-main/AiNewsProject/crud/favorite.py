from fastapi import Depends, HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from models import News
from models.favorite import Favorite
from schemas.favorite import FavoriteNewsItem
from schemas.news import NewsItemBase


async def is_news_favorite(
        user_id: int,
        news_id: int,
        db: AsyncSession = Depends(get_db)
) -> bool:
    """检查新闻是否收藏"""
    result = await db.execute(select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id))
    return result.scalar_one_or_none() is not None


async def add_news_favorite(
        user_id: int,
        news_id: int,
        db: AsyncSession = Depends(get_db)
) -> Favorite:
    """添加新闻收藏"""
    # 检查是否已经收藏
    existing_favorite = await is_news_favorite(user_id, news_id, db)
    if existing_favorite:
        # 如果已经收藏，返回现有收藏记录
        result = await db.execute(select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id))
        return result.scalar_one()

    # 创建新收藏
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return favorite


async def remove_news_favorite(
        user_id: int,
        news_id: int,
        db: AsyncSession = Depends(get_db)
) -> bool:
    """删除新闻收藏"""

    # 检查是否收藏
    existing_favorite = await is_news_favorite(user_id, news_id, db)
    if not existing_favorite:
        # 如果未收藏，返回错误
        raise HTTPException(status_code=404, detail="收藏不存在")

    # 删除收藏
    result = await db.execute(delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id))
    await db.commit()

    return result.rowcount > 0


async def get_news_favorite_list(
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        db: AsyncSession = Depends(get_db)
):
    """获取用户收藏列表"""
    # 总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 收藏的新闻总数
    
    # 获取收藏的新闻列表 - 联表查询 + 排序 + 分页
    query = (
        select(News, Favorite.created_at.label('favorite_time'))
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    result = await db.execute(query)
    favorite_news_list = result.all()
    
    # 构建响应数据 - 使用 Pydantic 模型类
    news_list = []
    for news, favorite_time in favorite_news_list:
        news_item_base = NewsItemBase.model_validate(news, from_attributes=True)
        news_data_dict = news_item_base.model_dump(mode='json')
        news_data_dict["favorite_time"] = favorite_time
        
        # 使用 FavoriteNewsItem 验证完整数据
        favorite_news_item = FavoriteNewsItem(**news_data_dict)
        
        # 转换为字典并使用别名
        news_data = favorite_news_item.model_dump(mode='json', by_alias=True)
        news_list.append(news_data)
    
    has_more = (page - 1) * page_size + len(news_list) < total
    
    return {
        "list": news_list,
        "total": total,
        "hasMore": has_more
    }


async def clear_news_favorite(
        user_id: int,
        db: AsyncSession = Depends(get_db)
) -> int:
    """清空用户收藏"""
    result = await db.execute(delete(Favorite).where(Favorite.user_id == user_id))
    await db.commit()

    return result.rowcount
