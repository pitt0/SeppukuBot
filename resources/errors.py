class StopException(BaseException):
    """Raised when someone recalls -stop command and the bot is already not spamming."""

class NoTimeException(BaseException):
    """Raised when a user does not set a timestamp for -remind"""

class InvalidTimestamp(BaseException):
    """Raised when the timestamp used by a user is not valid"""

class ItemNotFound(BaseException):
    """Raised when an item has not been found"""

class MonkeNotFound(BaseException):
    """Raised when a monke has not been found"""

class NoMonkeError(BaseException):
    """Raised when someone does not add a link when adding a monke"""

class WatchlistNotFound(BaseException):
    """Raised when someone types a watchlist that doesn't exist"""