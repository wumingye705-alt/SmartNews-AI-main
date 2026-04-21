from datetime import datetime

from pydantic import BaseModel, Field

from schemas.news import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite", description="是否收藏")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")

class FavoriteAddResponse(BaseModel):
    id: int = Field(..., description="收藏ID")
    news_id: int = Field(..., alias="newsId", description="新闻ID")

    class Config:
        from_attributes = True
        populate_by_name = True


class FavoriteNewsItem(NewsItemBase):
    favorite_time: datetime = Field(..., alias="favoriteTime", description="收藏时间")


