from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import CET
from src.extensions import server_db_
from sqlalchemy import select


def get_all_news_dict():
        result = server_db_.session.execute(
            select(News)
        ).scalars().all()
        return [news.to_dict() for news in result]


def get_all_unread_dict(user_id: int):
    result = server_db_.session.execute(
            select(News)
        ).scalars().all()
    
    return [news.to_dict() for news in result if str(user_id) not in news.seen_by.split("|")]


def get_news_by_id(id_: int):
    result = server_db_.session.get(News, id_)
    return result


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
    header: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=True)
    important: Mapped[str] = mapped_column(Text, nullable=False)
    grid_cols: Mapped[str] = mapped_column(Text, nullable=False)
    grid_rows: Mapped[str] = mapped_column(Text, nullable=False)
    info_cols: Mapped[str] = mapped_column(Text, nullable=False)
    info_rows: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    
    seen_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    accepted_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    
    tot_remarks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="news")
    
    def __init__(self, title: str, header: str, code: int, important: str, grid_cols: str, grid_rows: str, info_cols: str, info_rows: str, author: str):
        self.title = title
        self.header = header
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
    
    def grid_len(self) -> int:
        return len(self.grid_cols.split("|")) if self.grid_cols else 0
    
    def info_len(self) -> int:
        return len(self.info_cols.split("|")) if self.info_cols else 0
    
    def set_seen_by(self, user_id: int):
        if not str(user_id) in self.seen_by:
            self.seen_by += f"{user_id}|"
    
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
            "id": self.id,
            "title": self.title,
            "header": self.header,
            "code": self.code,
            "color": self.color,
            "important": self.important,
            "grid_cols": self._split(str(self.grid_cols)),
            "grid_rows": self._split(str(self.grid_rows)),
            "info_cols": self._split(str(self.info_cols)),
            "info_rows": self._split(str(self.info_rows)),
            "author": self.author,
            "seen_by": [num for num in self._split(str(self.seen_by)) if num],
            "accepted_by": self._split(str(self.accepted_by)),
            "tot_remarks": self.tot_remarks,
            "created_at": self.created_at.strftime("%d %b %Y @ %H:%M"),
        }


class Comment(server_db_.Model):
    """
    Comments table

    Columns:
    - ID: Unique identifier for the comment
    - TITLE: Title of the comment
    - CONTENT: Content of the comment
    - AUTHOR: Author of the comment
    - CREATED_AT: Timestamp of when the comment was created
    - NEWS_ID: Foreign key referencing the associated news article
    - NEWS: Relationship to the associated News object
    """
    __tablename__ = "comments"  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(75), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(25), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False)

    news: Mapped["News"] = relationship("News", back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment(id={self.id}, news_id={self.news_id}, author='{self.author}')"


if __name__ == "__main__":
    pass
