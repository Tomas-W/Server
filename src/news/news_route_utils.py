import bleach
from flask import session

def allow_only_styling(comment_content: str) -> str:
    allowed_tags = ["br", "strong", "em", "u"]
    replaced_comment = comment_content.replace("\n", "<br>")
    sanitized_comment = bleach.clean(replaced_comment, tags=allowed_tags, strip=True)
    return sanitized_comment


def clean_news_session():
    session.pop("form_errors", None)
    session.pop("form_data", None)
