"""
custom_errors.py
"""


class APIVersionNotFound(Exception):
    """An error related to a requested API version not being found."""


class ErrorObjectInRequest(Exception):
    """The response from the SystemLink service contained an error object."""


class ExpectedResponseError(Exception):
    """The response was not what was expected."""


class FeedExistsError(Exception):
    """The specified feed already exists."""


class FeedMissingError(Exception):
    """The specified feed was missing."""


class PackageUploadError(Exception):
    """There was an error when uploading a package."""


class RemoteCommandOutputNotEmpty(Exception):
    """The output of the remote command was not empty."""


class SuiteNotFound(Exception):
    """No suite was found within the provided date range or with the specified build version."""
