from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import CET
from src.extensions import server_db_
from sqlalchemy import select


def get_all_news():
        result = server_db_.session.execute(
            select(News)
        ).scalars().all()
        return [news.to_dict() for news in result]


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
    title: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=True)
    important: Mapped[str] = mapped_column(Text, nullable=False)
    grid_cols: Mapped[str] = mapped_column(Text, nullable=False)
    grid_rows: Mapped[str] = mapped_column(Text, nullable=False)
    info_cols: Mapped[str] = mapped_column(Text, nullable=False)
    info_rows: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    
    tot_remarks: Mapped[int] = mapped_column(Integer, default=0)
    tot_views: Mapped[int] = mapped_column(Integer, default=0)
    tot_accepted: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )

    remarks: Mapped[list["Remark"]] = relationship("Remark", back_populates="news")
    
    def __init__(self, title: str, code: int, important: str, grid_cols: str, grid_rows: str, info_cols: str, info_rows: str, author: str):
        self.title = title
        self.code = code
        self.color = self._get_color(code)
        self.important = important
        self.grid_cols = self._join(grid_cols)
        self.grid_rows = self._join(grid_rows)
        self.info_cols = self._join(info_cols)
        self.info_rows = self._join(info_rows)
        self.author = author

    def __repr__(self) -> str:
        return f"News(id={self.id}, title='{self.title}', code='{self.code}', important='{self.important}', author='{self.author}')"
    
    @staticmethod
    def _join(value: list[str]) -> str:
        return "|".join(value)
    
    @staticmethod
    def _split(value: str) -> list[str]:
        return value.split("|") if value else []
    
    @staticmethod
    def _get_color(code: int) -> str:
        if str(code).startswith("1"):
            return "blue"
        elif str(code).startswith("2"):
            return "orange"
        elif str(code).startswith("9"):
            return "red"
        else:
            return ""
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "code": self.code,
            "color": self.color,
            "important": self.important,
            "grid_cols": self._split(str(self.grid_cols)),
            "grid_rows": self._split(str(self.grid_rows)),
            "info_cols": self._split(str(self.info_cols)),
            "info_rows": self._split(str(self.info_rows)),
            "author": self.author,
        }


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


if __name__ == "__main__":
    pass
