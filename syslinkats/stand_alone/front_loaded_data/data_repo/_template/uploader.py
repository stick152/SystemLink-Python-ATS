"""
.. codeauthor:: Your Name <your.name@ni.com>

    This module is responsible for uploading data and/or files to a given SystemLink service via
    HTTP operations.

    **Instructions**

    * If you're reading this from the template:

      * Create a copy of the _template folder and rename it to the name of your service
        (similar to how we name buckets under tests/buckets.
      * Update the "codeauthor" directive value in this module documentation section to your
        name and email.

    * Place your data file (.json, .csv, etc.) into the folder containing this module.

    * Add your code to the upload function in this module.

      * The TestingHelper class will handle all HTTP operations (put, put_json, etc.).
      * If you need security keys, they can be created via the APIKeysManager class.

    .. code-block:: python
        :linenos:
        :caption: Example of Getting and using a Key
        :name: example-of-getting-using-key

        # Get your secret key and an instance of the APIKeysManager.
        # Note: Using 'with' will allow for automatic policy and key cleanup.
        with APIKeysManager.get_secret_key_simple(
            ats_config_data=ats_config_data,
            actions=['*']
        ) as api_keys_manager:
            # Use your secret key.
            url = 'your url'
            expected_response = 'whatever you expect to get as the response.code'
            self.get(url=url, expected_response=expected_response)
"""
from typing import Any, Dict

from syslinkats.framework.network_utils.http_verb_ops import HttpVerbOps
from syslinkats.framework.validators.validate_args import validate_args_for_value


def upload(ats_config_data: Dict[str, Any] = None, first_url_node: str = None) -> None:
    """Front-load data to a specific web service via HTTP operations.

    Args:
        ats_config_data (Dict[str, Any]): An instance of the config data used for testing.
        first_url_node (str): The first node (https://<server url>) of the URL to the server
        which hosts the service you wish to upload data to.

    Returns:
        None: None
    """
    validate_args_for_value(
        ats_config_data=ats_config_data,
        first_url_node=first_url_node,
        test_for_empty_false_zero=True
    )

    # Note: Use this HttpVerbOps instance for all HTTP operations.  The class has built-in error
    # handling as well as retry ability.  See the class' documentation and source for details.
    http_verb_ops = HttpVerbOps(
        username=ats_config_data['syslink_worker_username'],
        password=ats_config_data['syslink_worker_password'],
        enable_debug=True)

    # Todo: Place your code here.
