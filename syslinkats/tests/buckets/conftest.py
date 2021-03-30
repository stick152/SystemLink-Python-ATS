"""
conftest.py
"""
from typing import Dict

import pytest
from typing_extensions import Protocol

from syslinkats.tests.common.utils.testing_helper import TestingHelper


# pylint: disable=too-few-public-methods
class WaitForServiceProtocol(Protocol):
    """Defines the callback type of the callable returned by the remote_test_command fixture."""

    # pylint: disable=too-many-arguments
    def __call__(self, ats_config_data: Dict[str, str] = None, ping_url: str = None,
                 service_name: str = None, timeout: int = 30, post_connect_sleep_time: int = 1) \
            -> str:
        ...


@pytest.fixture(scope='package')
def wait_for_service_connection():
    """Wait for the service to connect."""
    def _wait_for_service_connection(ats_config_data: Dict[str, str] = None, ping_url: str = None,
                                     service_name: str = None, timeout: int = 30,
                                     post_connect_sleep_time: int = 1):
        with TestingHelper(worker_name=ats_config_data['syslink_worker_name'],
                           username=ats_config_data['syslink_worker_username'],
                           password=ats_config_data['syslink_worker_password']) as runner:
            runner.wait_for_service_to_connect(
                ping_url=ping_url.format(
                    http_prefix=ats_config_data['http_prefix'],
                    worker_name=ats_config_data['syslink_worker_name']
                ),
                service_name=service_name,
                timeout=timeout,
                post_connect_sleep_time=post_connect_sleep_time)
    return _wait_for_service_connection
