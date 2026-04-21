from sqlalchemy import (
    Integer, DateTime, ForeignKey,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from . import Base

class History(Base):
    """
    浏览历史表ORM模型
    """
    __tablename__ = 'history'

    __table_args__ = (
        Index('fk_history_user_idx', 'user_id'),          # 用户ID索引（核心筛选条件）
        Index('fk_history_news_idx', 'news_id'),          # 新闻ID索引
        Index('history_user_news_idx', 'user_id', 'news_id'),  # 联合索引（优化"用户+新闻"查询）
        Index('history_view_time_idx', 'view_time'),      # 时间索引（便于按浏览时间排序）
        {
            'comment': '浏览历史表',
            'mysql_charset': 'utf8mb4'
        }
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='历史ID'
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
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment='浏览时间'
    )

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, view_time={self.view_time})>"