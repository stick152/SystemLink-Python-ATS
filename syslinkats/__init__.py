"""
__init__.py
"""
import sys

from packaging import version

from syslinkats.data_file_retrievers import (
    ats_config_file,
    installation_config_file,
    instance_config_file,
    systemlink_server_config_file,
    user_config_file,
    alarm_config_file,
    workspaces_config_file,
    security_config_file,
    mongo_config_file
)

# Test for the supported version of python for the ATS framework.
MINIMUM_PYTHON_VERSION = '3.8.0'
SYS_PYTHON_VERSION = f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}'
if version.parse(SYS_PYTHON_VERSION) < version.parse(MINIMUM_PYTHON_VERSION):
    raise SystemError(f'This ATS requires the use of python version {MINIMUM_PYTHON_VERSION}.  '
                      'Please install this version of python and then run: '
                      'pip install -r requirements.txt.')
