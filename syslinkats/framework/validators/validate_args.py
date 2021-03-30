"""
validate_args.py
"""
import sys
from typing import Any

from syslinkats.framework.logging.auto_indent import AutoIndent

__author__ = 'sedwards'

LOGGER = AutoIndent(sys.stdout)


def validate_args_for_value(test_for_empty_false_zero: bool = False, **kwargs: Any) -> None:
    """Validate arguments in a kwargs dict.

    Args:
        test_for_empty_false_zero (bool): Whether or not to raise an error on empty, False or
        zero.  If False, then values will only be tested for None.
        **kwargs (Any): A dict of named keyword args to validate.

    Returns:
        None: None

    Raises:
        ValueError
    """
    error_args = []
    for key, value in kwargs.items():
        if test_for_empty_false_zero:
            if not value:
                LOGGER.write(f'{key} must not be empty, False, zero or None.')
                error_args.append(key)
                continue

        if value is None:
            LOGGER.write(f'{key} must not be None.')
            error_args.append(key)

    if error_args:
        raise ValueError(f'The following values must not be None or empty: {error_args}')
