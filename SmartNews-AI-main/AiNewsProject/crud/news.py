from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_cache import cache_with_redis, RedisCache
from models.news import Category, News

@cache_with_redis(prefix="category:list", expire=600)
async def get_category_list(db: AsyncSession, skip: int = 0, limit: int = 100):
    """获取新闻分类列表"""
    stmt = select(Category).offset(skip).limit(limit)
    result = (await db.execute(stmt)).scalars().all()
    return result

@cache_with_redis(prefix="news:list", expire=600)
async def get_news_list_by_category_id(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100):
    """获取新闻列表"""
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = (await db.execute(stmt)).scalars().all()
    return result

@cache_with_redis(prefix="news:detail", expire=1800)
async def get_new_details_by_news_id(db: AsyncSession, news_id: int):
    """根据新闻ID获取新闻详情"""
    # 获取新闻详情
    stmt = select(News).where(News.id == news_id)
    news_detail = (await db.execute(stmt)).scalar_one_or_none()

    return news_detail


async def add_views(db: AsyncSession, news_id: int) -> None:
    """增加新闻点击量"""
    # 增加新闻点击量
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    await db.execute(stmt)
    await db.commit()


async def news_commend(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    """推荐新闻"""
    stmt = select(News).where(
        (News.category_id == category_id and News.id != news_id)
    ).order_by(
        News.views.desc(), News.publish_time.desc()
    ).limit(limit)

    result = (await db.execute(stmt)).scalars().all()
    return result