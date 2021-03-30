"""
argparse_helpers.py

This module holds helper functions for use with argparse.

Some of these functions can be used for the "type" property for argparse::add_arguments
calls.  Simply pass the function name as such: type=<function name>.
"""
__author__ = 'sedwards'

import ast
from typing import Any, Dict, List, Optional, Tuple, Union

from _pytest.config import Config

from syslinkats.framework.validators.validate_args import validate_args_for_value
from syslinkats.tests.common.utils.testing_helper import TestingHelper


def bool_from_str(arg: Any) -> bool:
    """Take in an argument and try to return its bool equivalent.

    Args:
        arg (Any): This can be any type.  However, in general use it should be either a bool or
        str.

    Returns:
        bool: The bool equivalent of the passed in argument.  If the argument is not a str or
        bool, then False is returned.
    """
    if isinstance(arg, bool):
        return arg

    if isinstance(arg, str):
        if 'true' in arg.lower():
            return True
        return False

    # If any other type, just return False.
    return False


def int_from_str(arg: Any) -> int:
    """Take in an argument and try to return its int equivalent.

    Args:
        arg (Any): This can be any type.  However, in general use it should be either an int or
        str.

    Returns:
        int: The int equivalent of the passed in argument.  If the argument is not a str or
        int, then 0 is returned.
    """
    if isinstance(arg, int):
        return arg

    if isinstance(arg, str):
        try:
            value = int(arg)
        except ValueError:
            return 0

        return value

    # If any other type, just return 0.
    return 0


def literal_from_str(arg: Any) -> Any:
    """Take in a literal string and eval it."""
    if arg:
        try:
            return ast.literal_eval(arg)
        except (ValueError, SyntaxError):
            # This can happen if the arg is just a normal string or is a malformed object.
            # If so, just return the arg as-is.
            return arg

    return None


def get_val_from_arg_list(args_list: List[str], key: str, default: Any):
    """Parse an argparse args list for keys and return their associated value."""
    try:
        key_index = args_list.index(key)
        if len(args_list) > key_index:
            return args_list[key_index + 1]
        return default
    except ValueError:
        return default


def get_arg_dict(arg_list: Union[Optional[List[str]], Optional[str]] = None,
                 key_list: List[Tuple[str, Any]] = None,
                 config: Config = None) -> Dict[str, Any]:
    """Get a dict with key: value pairs from either a list of args, or the config object."""
    validate_args_for_value(key_list=key_list, config=config)
    arg_dict: Dict[str, Any] = {}
    if arg_list:
        if isinstance(arg_list, str):
            arg_list = TestingHelper.pass_through_args_converter(arg_list)
        for key in key_list:
            if key[0] in arg_list:
                key_value = get_val_from_arg_list(args_list=arg_list, key=key[0], default=key[1])
                if key_value is None:
                    key_value = config.getoption(key[0])
            else:
                key_value = config.getoption(key[0])
            arg_dict[key[0]] = key_value
    else:
        for key in key_list:
            key_value = config.getoption(key[0], default=key[1])
            arg_dict[key[0]] = key_value
    return arg_dict
