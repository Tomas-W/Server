from datetime import datetime
from functools import wraps
from typing import Callable

from src.extensions import server_db_, login_manager_

from config.settings import SERVER


@login_manager_.user_loader
def load_user(user_id):
    """Load the currently logged in Users information into the session."""
    from src.models.auth_model.auth_mod import User
    return server_db_.session.get(User, user_id)


def set_updated_at(func: Callable) -> Callable:
    """
    Decorator to set the updated_setting_at and last_setting_update attributes
    after executing the wrapped function.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.updated_setting_at = datetime.now(SERVER.CET)
        self.last_setting_update = f"{func.__name__}"
        return result
    return wrapper
