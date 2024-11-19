from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func
from src.extensions import server_db_
from config.settings import CET
from datetime import datetime


class EmailStrorage(server_db_.Model):
    """
    Stores data for periodic email notifications.
    
    - ID (int): Identifier [Primary Key]
    - EMAIL_TYPE (str): Type of email
    - RECIPIENT_EMAIL (str): Recipient's email address
    - NEWS_ID (int): Identifier of news item [Optional]
    - COMMENT_ID (int): Identifier of comment [Optional]
    - BAKERY_ID (int): Identifier of bakery item [Optional]
    - ADD_UPDATE (str): Item added or updated [Optional]
    """	
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True)
    email_type = Column(String(20), nullable=False)
    recipient_email = Column(String(100), nullable=False)
    news_id = Column(Integer, nullable=True)
    comment_id = Column(Integer, nullable=True)
    bakery_id = Column(Integer, nullable=True)
    add_update = Column(String(20), nullable=True)
    
    added_at = Column(DateTime, default=lambda: datetime.now(CET))
    
    def __init__(self, email_type: str, recipient_email: str, news_id: int,
                 comment_id: int, bakery_id: int, add_update: str):
        self.email_type = email_type
        self.recipient_email = recipient_email
        self.news_id = news_id
        self.comment_id = comment_id
        self.bakery_id = bakery_id
        self.add_update = add_update



    
