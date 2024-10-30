from datetime import datetime
from flask_login import current_user
from sqlalchemy import select, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.extensions import server_db_

from src.news.news_items import get_news_dict
from config.settings import CET


class News(server_db_.Model):
    """
    Stores the News data.

    - ID (int): Identifier [Primary Key]
    - TITLE (str): News title [Required]
    - HEADER (str): News header [Required]
    - CODE (int): News code [Required]
    - COLOR (str): News color [Required]
    - IMPORTANT (str): News important [Required]
    - GRID_COLS (str): News grid columns [Required] ['|' separated]
    - GRID_ROWS (str): News grid rows [Required] ['|' separated]
    - INFO_COLS (str): News info columns [Required] ['|' separated]
    - INFO_ROWS (str): News info rows [Required] ['|' separated]
    - AUTHOR (str): News author [Required]
    
    - SEEN_BY (str): User IDs [Default: ""] ['|' separated]
    - ACCEPTED_BY (str): User IDs [Default: ""] ['|' separated]
    - LIKED_BY (str): User IDs [Default: ""] ['|' separated]
    - DISLIKED_BY (str): User IDs [Default: ""] ['|' separated]
    
    - CREATED_AT (datetime): Timestamp of when the news article was created [Default: CET]
    
    - COMMENTS (list[Comment]): Relationship to the associated Comment object
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
    liked_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    disliked_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="news",
        cascade="all, delete-orphan, delete"
    )
    
    def __init__(self, title: str, header: str, code: int, important: str,
                 grid_cols: list[str], grid_rows: list[str], info_cols: list[str],
                 info_rows: list[str], author: str):
        """
        _cols and _rows are lists of strings that are joined
        with '|' to form a single string to be stored in the database.
        """	
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

    
    def grid_len(self) -> int:
        return len(self.grid_cols.split("|")) if self.grid_cols else 0
    
    def info_len(self) -> int:
        return len(self.info_cols.split("|")) if self.info_cols else 0
    
    def _get_grid_rows(self) -> list[list[str]]:
        """
        Sets up correct nesting for the grid rows to be
        properly displayed in the frontend.
        """	    
        grid_len = self.grid_len()
        row_list = []
    
        if grid_len:
            if grid_len == len(self.grid_rows.split("|")):
                list_ = self.grid_rows.split("|")
                row_list.append(list_)
            else:
                for i in range(0, len(self.grid_rows.split("|")), grid_len):   
                    row_list.append(self.grid_rows.split("|")[i:i + grid_len])

        return row_list
    
    def set_seen_by(self, user_id: int):
        if not str(user_id) in self.seen_by:
            self.seen_by += f"{user_id}|"
    
    def set_liked_by(self, user_id: int):
        self._remove_disliked_by(user_id)
        if not str(user_id) in self.liked_by:
            self.liked_by += f"{user_id}|"
    
    def set_disliked_by(self, user_id: int):
        self._remove_liked_by(user_id)
        if not str(user_id) in self.disliked_by:
            self.disliked_by += f"{user_id}|"
    
    def _remove_liked_by(self, user_id: int):
        self.liked_by = self.liked_by.replace(f"{user_id}|", "")
    
    def _remove_disliked_by(self, user_id: int):
        self.disliked_by = self.disliked_by.replace(f"{user_id}|", "")
    
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
        """
        Returns a dictionary representation of the News object
        for easy frontend display.
        """	
        return {
            "id": self.id,
            "title": self.title,
            "header": self.header,
            "code": self.code,
            "color": self.color,
            "important": self.important,
            "grid_cols": self._split(str(self.grid_cols)),
            "grid_rows": self._get_grid_rows(),
            "info_cols": self._split(str(self.info_cols)),
            "info_rows": self._split(str(self.info_rows)),
            "author": self.author,
            "seen_by": [num for num in self._split(str(self.seen_by)) if num],
            "accepted_by": self._split(str(self.accepted_by)),
            "liked_by": [num for num in self._split(str(self.liked_by)) if num],
            "disliked_by": [num for num in self._split(str(self.disliked_by)) if num],
            "created_at": self.created_at.strftime("%d %b %Y @ %H:%M"),
            "comments": [comment.to_dict() for comment in self.comments],
        }
    
    def __repr__(self) -> str:
        return (f"News:"
                f" (id={self.id},"
                f" title='{self.title}',"
                f" code='{self.code}',"
                f" important='{self.important}',"
                f" author='{self.author}')"
                )


def get_all_news_dict() -> list[dict]:
    result = server_db_.session.execute(
        select(News)
    ).scalars().all()
    return [news.to_dict() for news in result]


def get_all_unread_dict(user_id: int) -> list[dict]:
    result = server_db_.session.execute(
        select(News)
    ).scalars().all()
    return [news.to_dict() for news in result
            if str(user_id) not in news.seen_by.split("|")]


def get_news_by_id(id_: int):
    result = server_db_.session.get(News, id_)
    return result


def get_news_dict_by_id(id_: int):
    result = server_db_.session.get(News, id_)
    return result.to_dict()


def delete_news_by_id(id_: int) -> None:
    server_db_.session.delete(server_db_.session.get(News, id_))
    server_db_.session.commit()


def clear_news_db() -> None:
    server_db_.session.query(News).delete()
    server_db_.session.commit()


def _init_news() -> bool | None:
    if not server_db_.session.query(News).count():
        news_dict = get_news_dict()
        for _, item_details in news_dict.items():
            news_item = News(
                header=item_details["header"],
                title=item_details["title"],
                code=item_details["code"],
                important=item_details["important"],
                grid_cols=item_details["grid_cols"],
                grid_rows=item_details["grid_rows"],
                info_cols=item_details["info_cols"],
                info_rows=item_details["info_rows"],
                author=item_details["author"],
            )
            server_db_.session.add(news_item)
        server_db_.session.commit()
        return True
    
    return None
    
class Comment(server_db_.Model):
    """
    Stores the Comments data.

    - ID (int): Identifier [Primary Key]
    - CONTENT (str): Content of the comment [Required]
    - AUTHOR (str): Author of the comment [Required]
    - CREATED_AT (datetime): Timestamp of creation [Default: CET]
    
    - LIKED_BY (str): User IDs [Default: ""] ['|' separated]
    - DISLIKED_BY (str): User IDs [Default: ""] ['|' separated]
    
    - NEWS_ID (int): Foreign key referencing the associated news article
    - NEWS: Relationship to the associated News object
    """
    __tablename__ = "comments"  # noqa

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(25), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(CET)
    )
    
    liked_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    disliked_by: Mapped[str] = mapped_column(Text, nullable=True, default="")
    
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    news: Mapped["News"] = relationship("News", back_populates="comments")

    def __repr__(self) -> str:
        return (f"Comment:"
                f" (id={self.id},"
                f" news_id={self.news_id},"
                f" author='{self.author}')"
                )
    
    @staticmethod
    def _split(value: str) -> list[str]:
        return value.split("|") if value else []
    
    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Comment object
        for easy frontend display.
        """
        return {
            "id": self.id,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.strftime("%d %b %Y @ %H:%M"),
            "liked_by": [num for num in self._split(str(self.liked_by)) if num],
            "disliked_by": [num for num in self._split(str(self.disliked_by)) if num],
        }
    
    def set_liked_by(self, user_id: int) -> None:
        self._remove_disliked_by(user_id)
        if not str(user_id) in self.liked_by:
            self.liked_by += f"{user_id}|"
    
    def set_disliked_by(self, user_id: int) -> None:
        self._remove_liked_by(user_id)
        if not str(user_id) in self.disliked_by:
            self.disliked_by += f"{user_id}|"
    
    def _remove_liked_by(self, user_id: int) -> None:
        self.liked_by = self.liked_by.replace(f"{user_id}|", "")
    
    def _remove_disliked_by(self, user_id: int) -> None:
        self.disliked_by = self.disliked_by.replace(f"{user_id}|", "")


def get_comment_by_id(id_: int):
    result = server_db_.session.get(Comment, id_)
    return result


def add_new_comment(news_id: int, content: str) -> None:
    comment = Comment(
        content=content,
        author=current_user.username,
        news_id=news_id
    )
    server_db_.session.add(comment)
    server_db_.session.commit()
