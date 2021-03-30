"""
string_parse_helpers.py

This module contains helper functions for parsing data from strings.
"""
__author__ = 'sedwards'

from datetime import datetime
from typing import Union, Tuple


def parse_date_range(date_range: str) -> Union[datetime, Tuple[datetime, datetime]]:
    """Parse either a date string or date tuple from a string.

    Args:
        date_range (str): This can either be a string with a single date or a tuple string with
        a start and end date: i.e., "(01-15-2020, 01-30-2020)".
        Either way, the string date needs to be in the format %m-%d-%Y as that's how they're
        stored on the argohttp pages.
    """
    if '(' not in date_range:
        return datetime.strptime(date_range.strip(), '%m-%d-%Y')

    start_date_str = date_range[date_range.find('(') + 1: date_range.find(',')].strip()
    end_date_str = date_range[date_range.find(',') + 1: date_range.find(')')].strip()
    start_date = datetime.strptime(start_date_str, '%m-%d-%Y')
    end_date = datetime.strptime(end_date_str, '%m-%d-%Y')
    return start_date, end_date
