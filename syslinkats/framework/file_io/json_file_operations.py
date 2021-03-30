"""
json_file_operations.py

This module is responsible for operations related to json files.
"""
__author__ = 'sedwards'

import json
import paramiko
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any


def read_json_data_from_file(data_path: str, encoding: str = 'utf-8'):
    """Reads the contents of a json file into a dict object.

    Args:
        data_path (str): Path to the file.
        encoding (str): Inspected encoding of the file. (Default is 'utf-8')
    """
    config_data: Dict[str, Any] = {}
    if data_path and Path(data_path).exists():
        with Path(data_path).open(encoding=encoding) as fp_:
            config_data = json.loads(fp_.read())
    return config_data


def write_json_data_to_file(data_path: str,
                            data: Dict[str, Any],
                            encoding: str = 'utf-8',
                            indent: int = 2) -> None:
    """Writes the contents of a dict object to a JSON-encoded file.

    Args:
        data_path (str): Path to the file.
        data (Dict[str, Any]): Data to write to the file.
        encoding (str): Output file encoding. (Default is 'utf-8')
        indent (int): Specifies the indent level as a number of spaces for the generated JSON.
    """
    if data_path and Path(data_path).exists():
        with Path(data_path).open(mode='w', encoding=encoding) as fp_:
            json.dump(data, fp_, ensure_ascii=False, indent=indent)


def create_file_and_write_json_data_to_file(data_path: str,
                            data: Dict[str, Any],
                            encoding: str = 'utf-8',
                            indent: int = 2) -> None:
    """Writes the contents of a dict object to a JSON-encoded file.

    Args:
        data_path (str): Path to the file.
        data (Dict[str, Any]): Data to write to the file.
        encoding (str): Output file encoding. (Default is 'utf-8')
        indent (int): Specifies the indent level as a number of spaces for the generated JSON.
    """
    if data_path:
        with Path(data_path).open(mode='w+', encoding=encoding) as fp_:
            json.dump(data, fp_, ensure_ascii=False, indent=indent)