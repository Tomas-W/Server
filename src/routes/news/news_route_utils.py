import bleach

from flask import session


def allow_only_styling(content: str) -> str:
    """
    Sanitizes content to allow only styling tags.
    Replaces newlines with <br> tags.
    - Allowed tags: ["br", "strong", "em", "u"]
    """
    allowed_tags = ["br", "strong", "em", "u"]
    replaced_content = content.replace("\n", "<br>")
    sanitized_content = bleach.clean(replaced_content, tags=allowed_tags, strip=True)
    return sanitized_content


def clean_news_session():
    """
    Removes form errors and data from session.
    """
    session.pop("form_errors", None)
    session.pop("form_data", None)
