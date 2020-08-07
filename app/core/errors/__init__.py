import logging
from functools import wraps
from flask import abort
from flask_cognito import CognitoAuthError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


class ValidationError(AssertionError):
    def __init__(self, message):
        super().__init__(message)


# Flask-RESTPlus exception handlers not called properly,
# therefore implemented  custom approach with errors_handled decorator
# Waiting for Flask-RESTPlus 0.14.0 Release to solve this.
def error_handler(error):
    if isinstance(error, ValidationError):
        abort(400, str(error))
    elif isinstance(error, NoResultFound):
        abort(404, "not_found")
    elif isinstance(error, CognitoAuthError):
        if 'Invalid Cognito Authentication Token' in str(error):  # thrown from cognito middleware
            abort(401, 'error.auth.invalid_token')
        elif "Authorization Required - Request does not contain" in str(error):
            abort(401, 'error.auth.missing_token')
        else:
            abort(401, error.description)
    elif isinstance(error, HTTPException):
        # handled downstream
        raise error
    else:
        message = 'An unhandled exception occurred: ' + repr(error)
        log.exception(message, exc_info=True)
        abort(500, message)


def exception_to_response(func):
    @wraps(func)
    def with_exception_handling(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            return error_handler(ex)
    return with_exception_handling
