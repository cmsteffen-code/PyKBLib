"""Defines the various exceptions that are raised by PyKBLib."""


class KBLibException(Exception):
    """The base exception class for all PyKBLib exceptions.

    Attributes
    ----------
    message : str
        The error message sent with the exception.

    """

    def __init__(self, message):
        """Format the exception to include the returned error message.

        Parameters
        ----------
        message : str
            The error message returned by the Keybase API.

        """
        super(KBLibException, self).__init__(message)
        self.message = message


class APIException(KBLibException):
    """Raised when there's an error with the Keybase API."""


class KeybaseException(KBLibException):
    """Raised when there's an error with the Keybase class."""


class TeamException(KBLibException):
    """Raised when there's an error with the Team class."""
