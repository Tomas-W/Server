from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound, InternalServerError

class AbortBase(HTTPException):
    """Base class for custom abort exceptions with additional context support"""
    def __init__(self, description=None, go_to=None, **kwargs):
        super().__init__(description=description)
        self.go_to = go_to
        for key, value in kwargs.items():
            setattr(self, key, value)

class Abort400(AbortBase, BadRequest): 
    """400 Bad Request with additional context"""
    pass

class Abort401(AbortBase, Unauthorized): 
    """401 Unauthorized with additional context"""
    pass

class Abort403(AbortBase, Forbidden): 
    """403 Forbidden with additional context"""
    pass

class Abort404(AbortBase, NotFound): 
    """404 Not Found with additional context"""
    pass

class Abort498(AbortBase, BadRequest): 
    """498 Invalid Token with additional context"""
    pass

class Abort500(AbortBase, InternalServerError): 
    """500 Internal Server Error with additional context"""
    pass


def get_error_params(error):
    error_msg = error.description
    go_to = getattr(error, "go_to", None)
    extra_info = getattr(error, "extra_info", None)
    return error_msg, go_to, extra_info

