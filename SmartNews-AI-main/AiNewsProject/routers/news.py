from fastapi import APIRouter, Depends, Query, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from crud.news import get_category_list, get_news_list_by_category_id, get_new_details_by_news_id, add_views, \
    news_commend

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_news_categories(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    """获取新闻分类"""
    categories = await get_category_list(db=db, skip=skip, limit=limit)
    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": {
            "categories": categories
        }
    }


@router.get("/list")
async def get_news_list(
        db: AsyncSession = Depends(get_db),
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize")
        ):
    """获取新闻列表"""
    offset = (page - 1) * page_size
    news_list = await get_news_list_by_category_id(db=db, category_id=category_id, skip=offset, limit=page_size)
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": len(news_list),
            "hasMore": len(news_list) == page_size
        }
    }

@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="newsId"),
        db: AsyncSession = Depends(get_db)
):
    """获取新闻详情"""
    news_detail = await get_new_details_by_news_id(db=db, news_id=news_id)

    if news_detail is None:
        raise HTTPException(status_code=404)

    # 增加新闻点击量
    await add_views(db=db, news_id=news_id)

    # 推荐新闻
    related_news = await news_commend(db=db, news_id=news_id, category_id=news_detail.category_id)

    return {
            "code": 200,
            "message": "success",
            "data": {
                "id": news_detail.id,
                "title": news_detail.title,
                "content": news_detail.content,
                "image": news_detail.image,
                "author": news_detail.author,
                "publishTime": news_detail.publish_time,
                "categoryId": news_detail.category_id,
                "views": news_detail.views,
                "relatedNews": related_news
            }
        }
