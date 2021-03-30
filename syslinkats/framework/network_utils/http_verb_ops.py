"""
http_verb_ops.py

This module provides a wrapper for the requests library specific to our SystemLink ATS' http
operations.

Our service APIs should derive from this class.

NOTE: This is an example of how to use the custom processing functionality.
# Call the verb like so:
response = http_verb_ops.get(
    service_kwargs.pop('url', url),
    custom_handler=custom_handler,
    custom_handler_args={
        'http_verb_ops': http_verb_ops,
        'service_url': service_url
    }
)

# The custom function can be as follows:
def custom_handler(**kwargs):
    http_verb_ops: HttpVerbOps = kwargs.get('http_verb_ops', None)
    service_url: str = kwargs.get('service_url', None)
    if not http_verb_ops:
        raise KeyError('Missing http_verb_ops key in **kwargs.')
    if not service_url:
        raise KeyError('Missing service_url key in **kwargs.')

    if not http_verb_ops.request_response.ok:
        LOGGER.write(f'A non-zero status code was returned for url: {service_url}', 'error')
        error = HTTPError(
            url=service_kwargs.pop('url', url),
            code=http_verb_ops.request_response.status_code,
            msg=http_verb_ops.request_response.reason,
            hdrs=http_verb_ops.request_response.headers,
            fp=None
        )
        raise error

"""

__author__ = 'sedwards'

import functools
import json
import sys
import time
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.error import HTTPError

import requests
from requests import Response
from requests.auth import HTTPBasicAuth
from requests_file import FileAdapter

from syslinkats.framework.errors.custom_errors import (
    ErrorObjectInRequest,
    ExpectedResponseError
)
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.validators.validate_args import validate_args_for_value

LOGGER = AutoIndent(sys.stdout)


def _multi_try(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If the "retry_error_codes" arg was not supplied or was empty, then default to
        # 503: Service Unavailable
        if kwargs.get('retry_error_codes'):
            retry_error_codes = kwargs.pop('retry_error_codes', [503])
        else:
            retry_error_codes: List[int] = [503]

        # If the "retry_count" arg was not supplied or was empty, then default to 60.
        retry_count = kwargs.pop('retry_count', 60)

        while retry_count > 0:
            try:
                return func(*args, **kwargs)
            except HTTPError as http_error:
                if http_error.code in retry_error_codes:
                    retry_count -= 1
                    LOGGER.write(f'{http_error}: {retry_count} retries remaining.')
                    if retry_count == 0:
                        raise
                    time.sleep(10)
                else:
                    raise

    return wrapper


def _process_request_response(func):
    """ Processes the request response for errors and raises an exception if there are any.

    This function can also be called with a custom_handler which will do the handling instead
    of this function.
    """
    @functools.wraps(func)
    # pylint: disable=too-many-branches
    def wrapper(*args, **kwargs):
        if kwargs.get('custom_handler'):
            # Pop the custom kwargs off because the requests library cannot handle having any
            # unexpected kwargs.
            custom_handler = kwargs.pop('custom_handler')
            custom_handler_args = kwargs.pop('custom_handler_args', None)
            func_response = func(*args, **kwargs)
            custom_handler(**custom_handler_args)

            # Return the response object just in case someone is expecting it from a verb call.
            return func_response

        # These must be popped out before the func() call as requests is unable to handle
        # unexpected **kwargs elements.
        expected_success = kwargs.pop('expected_success', None)
        expected_response = kwargs.pop('expected_response', None)
        check_json_for_error_key = kwargs.pop('check_json_for_error_key', False)

        # Call the wrapped verb.
        func(*args, **kwargs)

        # If enabled, log output to file and console.
        if args[0].debug_output:
            if args[0].request_response is not None:
                if args[0].request_response.request is not None:
                    LOGGER.write(f'{args[0].request_response.request.method}: '
                                 f'{args[0].request_response.request.url}', 'debug')
                    if args[0].request_response.request.body:
                        LOGGER.write(f'Body: {args[0].request_response.request.body}', 'debug')
                LOGGER.write(f'Response: {args[0].request_response}', 'debug')
                try:
                    # Attempt to parse the response text and format it for output.
                    output = json.dumps(json.loads(args[0].request_response.text), indent=4)
                except (JSONDecodeError, TypeError):
                    # If there was an exception loading the text, then just output the response
                    # text as-is.
                    LOGGER.write(f'Response text: {args[0].request_response.text}', 'debug')
                else:
                    # If the text loaded and formatted okay, then output it.
                    LOGGER.write(f'Response text: {output}', 'debug')
            else:
                LOGGER.write('request_response was None or empty.', 'warning')

        # NOTE: request_response.ok calls raise_for_status() internally, so we don't need to
        # implement that option here.
        if expected_response is not None:
            if args[0].request_response.status_code != expected_response:
                raise ExpectedResponseError(
                    'Request failed with error: ({}) {}\r\nResponse text: {}.'.format(
                        args[0].request_response.status_code,
                        args[0].request_response.reason,
                        args[0].request_response.text
                    )
                )
        elif expected_success is not None and expected_success != args[0].request_response.ok:
            http_error = HTTPError(
                url=args[0].request_response.url,
                code=args[0].request_response.status_code,
                msg=args[0].request_response.reason,
                hdrs=args[0].request_response.headers,
                fp=None
            )
            LOGGER.write(http_error)
            raise http_error

        # If the request succeeded, but there's an error object in the response json, then raise
        # an exception.
        if check_json_for_error_key:
            response_json = args[0].request_response.json()
            if 'error' in response_json and response_json['error']:
                raise ErrorObjectInRequest(
                    'Response contained the following error: ({}) {}:  {}'.format(
                        response_json['error'].get('code', 0),
                        response_json['error'].get('name', 'Name not found.'),
                        response_json['error'].get('message', 'Message not found.')
                    )
                )

        # Return the response object just in case someone is expecting it from a verb call.
        return args[0].request_response
    return wrapper


# pylint: disable=too-many-instance-attributes
class HttpVerbOps:
    """The base class for all SystemLink service access classes."""

    def __init__(self, username: str = None, password: str = None,
                 headers: Optional[Dict[str, str]] = None,
                 enable_debug: Optional[bool] = False):
        """Initialize an instance of HttpVerbOps.

        Args:
            username (str): The username to use for the specified master.
            password (str): The password to use for the specified master.
            headers (Dict[str, str]): The headers for the request.
            enable_debug (bool): Whether or not to use debug output with requests.
        """
        requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member
        # Set up a session with a file adapter so that we can GET local files through URLs.
        self._session = requests.Session()
        self._session.mount('file://', FileAdapter())

        validate_args_for_value(username=username, password=password)
        self._username: str = username
        self._password: str = password
        self._headers: Dict[str, str] = {
            'Content-Type': 'application/json',
            'x-ni-api-key': None
        } or headers
        self._request_response: Optional[Response] = None
        self._debug_output: bool = enable_debug
        self._auth: HTTPBasicAuth = HTTPBasicAuth(self._username, self._password)

    def __enter__(self):
        """This allows this class to be called using the 'with' keyword.
        For example:
            with <DerivedClassName>() as <short_name>:
                ...
        """
        # NOTE: Do any special connection-specific stuff here (such as CA).
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """When called using the 'with' keyword and no longer in scope, this method will be
        called.

        NOTES:
        * In order to be called, all 4 positional args must be present.
        * Do any cleanup or disconnecting here.
        * Handle any exceptions here (optional).
        """

    # region Properties
    @property
    def request_response(self) -> Response:
        """Getter for the request response."""
        return self._request_response

    @request_response.setter
    def request_response(self, value: Response) -> None:
        """Setter for the request response."""
        self._request_response = value

    @property
    def debug_output(self) -> bool:
        """Getter for the '_debug_output' flag."""
        return self._debug_output

    @debug_output.setter
    def debug_output(self, value: bool) -> None:
        """Setter for the '_debug_output' flag."""
        self._debug_output = value

    @property
    def headers(self) -> Dict[str, Any]:
        """Getter for the '_headers' attribute."""
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, Any]) -> None:
        """Setter for the '_headers' attribute."""
        self._headers = value

    @property
    def x_ni_api_key(self) -> str:
        """Getter for the 'x-ni-api-key' attribute of '_headers'."""
        return self._headers.get('x-ni-api-key', None)

    @x_ni_api_key.setter
    def x_ni_api_key(self, value: str) -> None:
        """Setter for the 'x-ni-api-key' attribute of '_headers'."""
        self._headers['x_ni_api_key'] = value

    @property
    def basic_auth(self) -> HTTPBasicAuth:
        """Getter for the '_auth' attribute."""
        return self._auth

    @basic_auth.setter
    def basic_auth(self, value: Union[HTTPBasicAuth, Tuple[str, str]]) -> None:
        """Setter for the '_auth' attribute."""
        self._auth = value
    # endregion

    # region Verbs
    @_multi_try
    @_process_request_response
    def delete(self, url: str, **kwargs) -> Response:
        """Makes a DELETE request to the specified URL."""
        self.request_response = self._session.delete(
            url=url,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def get(self, url: str, **kwargs) -> Response:
        """Makes a GET request to the specified URL."""
        self.request_response = self._session.get(
            url=url,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def head(self, url: str, **kwargs) -> Response:
        """Makes a HEAD request to the specified URL."""
        self.request_response = self._session.head(
            url=url,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def options(self, url: str, **kwargs) -> Response:
        """Makes an OPTIONS request to the specified URL."""
        self.request_response = self._session.options(
            url=url,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def patch(self, url: str, data: Any, **kwargs) -> Response:
        """Makes a PATCH request to the specified URL."""
        self.request_response = self._session.patch(
            url=url,
            data=data,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def patch_json(self, url: str, json_: Dict, **kwargs) -> Response:
        """Makes a PATCH request to the specified URL with a JSON payload."""
        self.request_response = self._session.patch(
            url=url,
            json=kwargs.pop('json_', json_),
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def post(self, url: str, data: Any, **kwargs) -> Response:
        """Makes a POST request to the specified URL."""
        self.request_response = self._session.post(
            url=url,
            data=data,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def post_files(self, url: str, files: Dict, **kwargs) -> Response:
        """Makes a POST request to the specified URL with a file payload."""
        _headers = kwargs.pop('headers', self._headers.copy())
        _headers.pop('Content-Type', None)
        self.request_response = self._session.post(
            url=url,
            files=kwargs.pop('files', files),
            headers=_headers,
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def post_json(self, url: str, json_, **kwargs) -> Response:
        """Makes a POST request to the specified URL with a JSON payload."""
        self.request_response = self._session.post(
            url=url,
            json=kwargs.pop('json_', json_),
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def put_json(self, url: str, json_: Dict, **kwargs) -> Response:
        """Makes a PUT request to the specified URL with a JSON payload."""
        self.request_response = self._session.put(
            url=url,
            json=kwargs.pop('json_', json_),
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response

    @_multi_try
    @_process_request_response
    def put(self, url: str, data: Any, **kwargs) -> Response:
        """Makes a PUT request to the specified URL."""
        self.request_response = self._session.put(
            url=url,
            data=data,
            headers=kwargs.pop('headers', self._headers),
            auth=kwargs.pop('auth', self._auth),
            verify=kwargs.pop('verify', False),
            **kwargs
        )
        return self.request_response
    # endregion
