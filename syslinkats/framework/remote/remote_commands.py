"""
remote_commands.py

This module contains functions for running remote commands, specifically on AWS instances.
"""
__author__ = 'sedwards'

import sys
import time
from typing import List

from syslinkats.framework.aws.aws_instance import AWSInstance
from syslinkats.framework.errors.custom_errors import RemoteCommandOutputNotEmpty
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.validators.validate_args import validate_args_for_value

LOGGER = AutoIndent(sys.stdout)


# pylint: disable=too-many-arguments
def run_aws_remote_command(region_name: str = None,
                           target_public_dns_names: List[str] = None,
                           instance_ids: List[str] = None,
                           remote_command: str = None,
                           output_ignore_list: List[str] = None,
                           total_command_run_time: int = 30,
                           retry_count: int = 3,
                           platform_type: str = 'Windows'):
    """Run a command on a remote AWS instance.

    Args:
        region_name (str): The AWS region where your instances reside.
        target_public_dns_names (List[str]): The public DNS name of the target
        system.
        instance_ids (List[str]): (OPTIONAL) The instance Ids of the target instance.
        remote_command (str): The command string to run on the remote AWS instance.
        output_ignore_list (List[str]): A list of output error / warning codes to ignore
        when processing the command output.
        total_command_run_time (int): The total time (seconds) allowed for commands to run on
        all target instances.
        retry_count (int): The number of times to retry the remote command.
        platform_type (str): Target platform for the command. Either 'Windows' or 'Linux'. Defaults to 'Windows'.

    Returns:
        str: The standard output if that was provided; otherwise empty

    Raises:
        Exception: Any and all exceptions raised by the remote command.
    """
    validate_args_for_value(
        region_name=region_name,
        remote_command=remote_command,
        total_command_run_time=total_command_run_time
    )

    if not target_public_dns_names and instance_ids:
        raise ValueError('You must provide either public DNS names or instance Ids.')

    # Instantiate an AWSInstance in order to run commands, etc.
    aws_instance = AWSInstance(region_name=region_name)
    # Get the instance Id of the worker instance.
    if not instance_ids:
        instance_ids = aws_instance.describe_instance_ids(
            filters=[
                {
                    'Name': 'network-interface.private-dns-name',
                    'Values': AWSInstance.public_dns_names_to_private(
                        target_public_dns_names)
                }],
            newest_only=False)

    # Make sure that we have an ignore list to check, even if empty.
    if not output_ignore_list:
        output_ignore_list = []

    for retry_index in range(retry_count):
        # Run the remote command.
        LOGGER.write(f'Running remote command on {target_public_dns_names}: {remote_command}')
        try:
            output = aws_instance.send_commands(
                instance_ids=instance_ids,
                commands=[remote_command],
                total_command_run_time=total_command_run_time,
                return_standard_output=True,
                platform_type=platform_type
            )
        except TimeoutError:
            # If the command timed out, try running it again.
            continue

        if isinstance(output, str):
            return output

        # If there's any output and any contained error / warning codes or names, etc. are not
        # in the ignore list, then raise an exception.
        elif output:
            ignore_output = any(_ in output for _ in output_ignore_list)
            if not ignore_output:
                if retry_index == retry_count - 1:
                    LOGGER.write(output, 'exception')
                    raise RemoteCommandOutputNotEmpty(output)
                else:
                    LOGGER.write(f'Retrying remote command on '
                                 f'{target_public_dns_names}: {remote_command}')
            else:
                break
        elif not output:
            break

        time.sleep(10)
