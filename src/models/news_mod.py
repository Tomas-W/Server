from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import CET
from src.extensions import server_db_


class News(server_db_.Model):
    """
    News table

    - ID: Unique identifier for the news article
    - TITLE: Title of the news article
    - CONTENT: Content of the news article
    - AUTHOR: Author of the news article
    - TOT_REMARKS: Total number of remarks on the news article
    - REMARKS: String containing remarks on the news article
    - CREATED_AT: Timestamp of when the news article was created
    - TOT_VIEWS: Total number of views for the news article
    - TOT_ACCEPTED: Total number of acceptances for the news article
    """
    __tablename__ = 'news'  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(75), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(25), nullable=False)
    tot_remarks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )
    tot_views: Mapped[int] = mapped_column(Integer, default=0)
    tot_accepted: Mapped[int] = mapped_column(Integer, default=0)

    remarks: Mapped[list["Remark"]] = relationship("Remark", back_populates="news")

    def __repr__(self) -> str:
        return f"News(id={self.id}, title='{self.title}', author='{self.author}')"


class Remark(server_db_.Model):
    """
    Remarks table

    Columns:
    - ID: Unique identifier for the remark
    - TITLE: Title of the remark
    - CONTENT: Content of the remark
    - AUTHOR: Author of the remark
    - CREATED_AT: Timestamp of when the remark was created
    - NEWS_ID: Foreign key referencing the associated news article
    - NEWS: Relationship to the associated News object
    """
    __tablename__ = "remarks"  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(75), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(25), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False)

    news: Mapped["News"] = relationship("News", back_populates="remarks")

    def __repr__(self) -> str:
        return f"Remark(id={self.id}, news_id={self.news_id}, author='{self.author}')"
