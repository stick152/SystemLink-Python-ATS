"""
general_directory_ops.py
"""
import glob
import shutil
import sys
from os import access, W_OK, chmod, path, makedirs
from typing import Optional

from syslinkats.framework.logging.auto_indent import AutoIndent

# Set up AutoIndent for logging.
LOGGER = AutoIndent(stream=sys.stdout)


def clear_directory(directory_path: Optional[str]) -> bool:
    if path.exists(directory_path):
        try:
            shutil.rmtree(directory_path, False, onerror=on_error)
        except Exception as ex:
            LOGGER.write(str(ex), 'exception')
            raise
        return True
    return False


def clear_or_create_directory(directory_path: Optional[str]) -> None:
    """ Clears out or creates the local feed / suite staging folder.

    Args:
        directory_path: The path to the local staging directory.

    Raises:
        Any and all Exceptions.

    Returns:
        None: None
    """
    if not clear_directory(directory_path):
        makedirs(directory_path)


def do_path_parameter_validation(is_dir: bool = True, param_name: str = None,
                                 param_value: str = None):
    """Verify that a path parameter is actually valid.

    Args:
        is_dir: Whether or not the param_value should be a directory.
        param_name: The name of the parameter.
        param_value: The parameter's value.

    Raises:
        ValueError
        FileNotFoundError
        NotADirectoryError
        IsADirectoryError
    """
    if param_value is None or param_value == '':
        LOGGER.write('{} was not valid.'.format(param_name), 'error')
        raise ValueError('{} was not valid.'.format(param_name))

    if not path.exists(param_value):
        LOGGER.write('{} "{}" did not exist.'.format(param_name, param_value), 'error')
        raise FileNotFoundError('{} "{}" did not exist.'.format(param_name, param_value))

    if is_dir:
        if not path.isdir(param_value):
            LOGGER.write('{} "{}" must be a directory.'.format(param_name, param_value), 'error')
            raise NotADirectoryError('{} "{}" must be a directory.'.format(
                param_name, param_value))
    else:
        if path.isdir(param_value):
            LOGGER.write('{} "{}" is a directory.'.format(param_name, param_value), 'error')
            raise IsADirectoryError('{} "{}" is a directory.'.format(param_name, param_value))


def get_newest_directory(parent_directory_path: Optional[str], filter_by_date: bool = True) -> str:
    """Get the path to the newest directory in a parent directory.

    Args:
        parent_directory_path: The path to the directory where the
            directories to filter are contained.
        filter_by_date:  Whether or not to filter by date.  If False, filter by modified time.

    Returns:
        The path to the newest subdirectory in a directory.

    Raises:
        NotADirectoryError
        ValueError
    """
    do_path_parameter_validation(
        is_dir=True,
        param_name='parent_directory_path',
        param_value=parent_directory_path
    )

    return max(
        glob.glob(path.join(parent_directory_path, '*/')),
        key=path.getctime if filter_by_date else path.getmtime
    )


def on_error(raising_function, path_name, exc_info) -> None:
    """Error handler for shutil.rmtree.

      If the error is due to an access error (read only file)
      it attempts to add write permission and then retries.

      If the error is for another reason it re-raises the error.

      Usage : shutil.rmtree(path, onerror=on_error)

    Args:
        raising_function: The function which raised the exception.
        path_name: The path name passed to raising_function.
        exc_info: The exception information raised by sys.exc_info().

    Raises:
        Exception: The passed-in exception.

    Returns:
        None: None
    """
    import stat
    if not access(path_name, W_OK):
        # Is the error an access error ?
        chmod(path_name, stat.S_IWUSR)
        raising_function(path_name)
    else:
        raise exc_info
