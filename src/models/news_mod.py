from datetime import datetime

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

    id = server_db_.Column(server_db_.Integer, primary_key=True)
    title = server_db_.Column(server_db_.String(75), nullable=False)
    content = server_db_.Column(server_db_.Text, nullable=False)
    author = server_db_.Column(server_db_.String(25), nullable=False)
    tot_remarks = server_db_.Column(server_db_.Integer, default=0)

    created_at = server_db_.Column(server_db_.DateTime,
                                   default=lambda: datetime.now(CET))
    tot_views = server_db_.Column(server_db_.Integer, default=0)
    tot_accepted = server_db_.Column(server_db_.Integer, default=0)

    remarks = server_db_.relationship("Remark", back_populates="news")

    def __repr__(self):
        return f"News(id={self.id}, title={self.title}, author={self.author})"


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

    id = server_db_.Column(server_db_.Integer, primary_key=True)
    title = server_db_.Column(server_db_.String(75), nullable=False)
    content = server_db_.Column(server_db_.Text, nullable=False)
    author = server_db_.Column(server_db_.String(25), nullable=False)

    created_at = server_db_.Column(server_db_.DateTime,
                                   default=lambda: datetime.now(CET))
    news_id = server_db_.Column(server_db_.Integer, server_db_.ForeignKey("news.id"),
                                nullable=False)

    news = server_db_.relationship("News", back_populates="remarks")

    def __repr__(self):
        return f"Remark(news_id={self.news_id}, author={self.author})"
