from sqlalchemy import (
    Integer, DateTime, ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from . import Base

class Favorite(Base):
    """
    收藏表ORM模型
    """
    __tablename__ = 'favorite'

    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'), # 联合唯一索引
        Index('fk_favorite_user_idx', 'user_id'),
        Index('fk_favorite_news_idx', 'news_id'),
        {
            'comment': '收藏表',
            'mysql_charset': 'utf8mb4'
        }
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='收藏ID'
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        comment='用户ID'
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('news.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        comment='新闻ID'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment='收藏时间'
    )

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, created_at={self.created_at})>"