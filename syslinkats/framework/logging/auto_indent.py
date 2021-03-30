#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auto_indent
"""

import inspect
import logging
import os

__author__ = 'sedwards'

from typing import Any


class AutoIndent:
    """Indent debug output based on function call depth."""

    # pylint: disable=too-many-arguments
    def __init__(self,
                 stream=None,
                 file_name: str = 'systemlink_test_output.log',
                 file_mode: str = 'w',
                 level: int = logging.INFO,
                 log_format: str = '[%(asctime)s] {%(pathname)s:%(lineno)d} %('
                 'levelname)s - %(message)s',
                 date_format: str = '%m/%d/%Y %I:%M:%S %p'):
        """Initialize the class.

        Args:
            stream:
            file_name:
            file_mode:
            level:
            log_format:
            date_format:
        """
        if not stream:
            raise TypeError('*** You must provide a stream.')

        logging.basicConfig(
            filename=file_name,
            filemode=file_mode,
            level=level,
            format=log_format,
            datefmt=date_format
        )
        logging.raiseExceptions = False

        self.stream = stream
        self.depth = len(inspect.stack())
        self.logger = logging.getLogger(__name__)
        self.logger.raiseExceptions = False

    def indent_level(self) -> int:
        """Assigns the indentation level."""
        return len(inspect.stack()) - self.depth

    def write(self, data: Any, log_method: str = 'info'):
        """Write debug output to the specified stream.

        Args:
            data:  The output to write.
            log_method: The logging method to call (logging.info,
            logging.error, etc.)
        """
        # """Write debug output to the specified stream.
        #
        # :param data: The output to write.
        # """
        indentation = '*** ' * self.indent_level()

        def indent(level: str) -> str:
            """Indent the line by a specified amount.

            :type level: int
            :param level: Level of indentation for written data.
            :return: The level of indentation for this data.
            """
            if level:
                return indentation + level
            return level

        data = str(data)
        raw_data = data
        data = os.linesep.join([indent(line) for line in data.split('\n')])

        try:
            self.stream.write(data)
        except UnicodeEncodeError:
            self.stream.write(
                'A unicode encoding error occurred when attempting to write to the stream.')

        self.stream.write(os.linesep)
        self.stream.flush()

        log_method = log_method.lower()
        try:
            if log_method == 'info':
                self.logger.info(raw_data, stacklevel=2)
            elif log_method == 'warning':
                self.logger.warning(raw_data, stacklevel=2)
            elif log_method == 'error':
                self.logger.error(raw_data, stacklevel=2)
            elif log_method == 'exception':
                self.logger.exception(raw_data, stacklevel=2)
            elif log_method == 'debug':
                self.logger.debug(raw_data, stacklevel=2)
            else:
                self.logger.info(raw_data, stacklevel=2)
        except UnicodeEncodeError:
            self.logger.warning(
                'A unicode encoding error occurred when attempting to log the data.')
