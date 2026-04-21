from datetime import datetime

from pydantic import BaseModel, Field

from schemas.news import NewsItemBase


class HistoryItem(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")


class HistoryNewsItem(NewsItemBase):
    view_time: datetime = Field(..., alias="viewTime", description="浏览时间")
