"""
dotted_dict.py
"""
from __future__ import annotations
# TODO: Get rid of the above when we switch to Python 4.0.  This is needed for the .copy method
#  in order to specify the DottedDict return type.

__author__ = 'sedwards'

from json import JSONEncoder
from typing import Any, Dict, List, Optional, Union

from syslinkats.framework.validators.validate_args import validate_args_for_value


# region JSONEncoder default Setup
# When json.dumps() is used to print the DottedDict as a string, the following code will cause
# the 'default' encoding function for JSONEncoder to be set to the _default function below.
# This allows DottedDict to be json serializable, at least in the scope of dumping to a string.

# NOTE: This is also defined in the main __init__.py for the SysLink ATS.  However, I also have
# it here in case someone wants to use this module outside of the ATS.

# pylint: disable=unused-argument
def _default(json_encoder_instance, obj):
    # Note that we don't use json_encoder_instance, but it must be there for the JSONEncoder
    # call in json.dumps() to work.
    return getattr(obj.__class__, "json_serializable", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default
# endregion


class DottedDict:
    """A recursive class for converting dicts to class-like objects that support dot notation."""

    def __init__(self, dict_: Dict[str, Any] = None) -> None:
        """Initialize the class by converting the dict to a class-like object."""
        validate_args_for_value(dict_=dict_)
        for key, val in dict_.items():
            if isinstance(key, int):
                # Dict keys which were number strings may be eval'd into ints during this
                # process.  In that case, be sure to cast them back to str.
                key = str(key)
            setattr(self, key, val)

    def json_serializable(self) -> Dict[str, Any]:
        """Returns a json-serializable object.  In this case, a dict.

        Notes:
            The JSONEncoder section at the top of this module uses this function for making this
            class json serializable.

        Returns:
            Dict[str, Any]
        """
        return self.__dict__

    def __getitem__(self, item: str = None) -> Any:
        """Return an item in the object's __dict__.

        Args:
            item (str): The item (key) to get in the object's dict.

        Returns:
            Any
        """
        validate_args_for_value(item=item, test_for_empty_false_zero=True)
        return self.__dict__.get(item, None)

    def __setitem__(self, key: str = None, value: Optional[Any] = None) -> None:
        """Sets the value of one of this object's attributes.

        Args:
            key (str): The attribute name at which to add or set a value.
            value (Any): The value to set to the attribute.

        Returns:
            None
        """
        validate_args_for_value(key=key, test_for_empty_false_zero=True)
        setattr(self, key, self.__class__(value) if isinstance(value, dict) else value)

    def __setattr__(self, key: str = None, value: Optional[Any] = None) -> Optional[List[str]]:
        """Adds a new attribute or sets the value of an existing one, converting it if it's a dict.

        This allows for users to add new attributes to objects of this type (or set values of
        existing attributes) by using dot notation.

        Args:
            key (str): The attribute name at which to add or set a value.
            value (Any): The value to set to the attribute.

        Returns:
            Optional[List[str]]
        """
        validate_args_for_value(key=key, test_for_empty_false_zero=True)
        if isinstance(value, dict):
            self.__dict__[key] = self.__class__(value)
        elif isinstance(value, list):
            tmp = []
            for item in value:
                if isinstance(item, dict):
                    tmp.append(self.__class__(item))
                elif isinstance(item, list):
                    tmp.append(self.__setattr__(None, item))
                else:
                    tmp.append(item)
            if key is None:
                return tmp
            self.__dict__[key] = tmp
        else:
            self.__dict__[key] = value
        return None

    def __iter__(self) -> Any:
        """Allow this object to be iterable.

        Yields:
            Any
        """
        for item in self.__dict__.items():
            yield item

    def __repr__(self) -> str:
        """The handler for str representations of this object."""
        return '{%s}' % ', '.join('%s: %s' % (k, repr(v)) for (k, v) in self.__dict__.items())

    def copy(self) -> DottedDict:
        """Return a shallow copy of this object."""
        return self.__class__(self.__dict__.copy())

    def get(self, val: Union[str, List[str]] = None, default: Optional[Any] = None,
            delimiter: str = '.') -> Any:
        """Return an item in the object's __dict__.

        In essence, this "get" method allows the user to pass in a delimited string which acts
        as a path to an attribute.  Passing in string with no delimiters is akin to a root path.
        In other words, the attribute to retrieve is top-level.

        Passing in a delimited string results in the creation of a list of attributes which this
        method will then iterate through, drilling down into a tree of attributes until it
        reaches the leaf node which it then returns.

        Args:
            val (Union[str, List[str]]): Either a string or list of strings used to query this
            object for an attribute.
            default (Any): The default value to return when the get operation fails to find
            anything with the specified key.
            delimiter (str): A delimiter used to break up a query index string into a list of
            index strings.

        Returns:
            Any

        Raises:
            AttributeError
            TypeError
            KeyError
        """
        validate_args_for_value(val=val, test_for_empty_false_zero=True)
        try:
            attributes = val
            if isinstance(val, str):
                if delimiter in val:
                    attributes = val.split(delimiter)
                else:
                    return self.__getitem__(val)

            if isinstance(attributes, list):
                # For each element in the list of attributes, set the object to "get" from to
                # the one obtained from the get.  Do this until the end of the attributes list.
                parameter_properties = self
                for attribute in attributes:
                    try:
                        parameter_properties = parameter_properties.get(attribute)
                    except AttributeError:
                        raise AttributeError(f'The parameter did not contain the "{attribute}" '
                                             'attribute.')
                return parameter_properties

            raise TypeError('val may only be of type str or list.')
        except KeyError:
            return default

    def set(self, key: str = None, value: Optional[Any] = None) -> None:
        """Sets the value of an item in the object's __dict__.

        Args:
            key (str): The string index of the element to set a value on.
            value (Any): The value to set the located element to.

        Returns:
            None
        """
        validate_args_for_value(key=key, test_for_empty_false_zero=True)
        self.__setitem__(key, value)

    @property
    def dict(self) -> Dict[str, Any]:
        """A property for accessing this object as a dict."""
        tmp = {}
        for key, val in self.__dict__.items():
            if isinstance(val, DottedDict):
                tmp[key] = val.dict
            else:
                tmp[key] = val
        return tmp
