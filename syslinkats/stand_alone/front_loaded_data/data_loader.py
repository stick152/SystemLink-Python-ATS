"""
.. codeauthor:: Shawn Edwards <shawn.edwards@ni.com>

This module iterates through the buckets in the data_repo folder.  If it finds a folder (other
than _template) which contains the uploader.py module, then it calls that module's upload
function to begin the front-loading process.

Notes:
    The ATS calls this module as part of its daily and test-day instance setup process.
"""
import argparse
import importlib.util
import os
import sys
from typing import Any, Dict

from syslinkats import ats_config_file
from syslinkats.framework.common.argparse_helpers import bool_from_str
from syslinkats.framework.file_io.json_file_operations import read_json_data_from_file
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.validators.validate_args import validate_args_for_value

LOGGER: AutoIndent = AutoIndent(stream=sys.stdout)
MODULE_TITLE: str = "uploader"
MODULE_NAME: str = "uploader.py"
REPO_FOLDER_NAME: str = "data_repo"


def call_uploaders(ats_config_data: Dict[str, Any] = None) -> None:
    """Iterates over the data_repo folder, looking for data buckets to handle.

    If it finds a valid bucket, the function will look for a module called uploader.py
    If this module contains a function called "upload", then it will call that function.

    Args:
        ats_config_data (Dict[str, Any]): An instance of the config data used for testing.

    Returns:
        None: None
    """
    validate_args_for_value(ats_config_data=ats_config_data)

    # Iterate through all the buckets in the REPO_FOLDER_NAME folder.
    dir_name = os.path.join(os.path.dirname(__file__), REPO_FOLDER_NAME,)
    for bucket in list(
        filter(lambda x: os.path.isdir(os.path.join(dir_name, x)), os.listdir(dir_name))
    ):
        if bucket.startswith("_"):
            continue

        path_to_uploader = os.path.join(dir_name, bucket, MODULE_NAME)
        if os.path.exists(path_to_uploader):
            # Import the module in a manner which supports relative imports.
            spec = importlib.util.spec_from_file_location(
                MODULE_TITLE, path_to_uploader
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Call the upload function in the uploader module.
            module.upload(
                ats_config_data=ats_config_data,
                first_url_node=f'{ats_config_data["http_prefix"]}://'
                f'{ats_config_data["syslink_worker_name"]}',
            )


if __name__ == "__main__":
    # pylint: disable=pointless-string-statement
    """The main entry point for this module when run as a script.

    .. note::
        This function is for testing and/or manual execution.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ats-config-path",
        action="store",
        type=str,
        default=ats_config_file(),
        dest="ats_config_path",
        help="""The path to the JSON file with the configuration for the dev master.""",
    )
    parser.add_argument(
        "--use-dev-worker",
        action="store",
        type=bool_from_str,
        default=False,
        dest="use_dev_worker",
        help="""Tells the runners that you want to test using the syslink_worker_name
            specified in default_conf.json instead of the auto-detected AWS ATS instance(s).""",
    )
    args, _ = parser.parse_known_intermixed_args()

    ats_config_data_ = read_json_data_from_file(args.ats_config_path)

    call_uploaders(ats_config_data_)
