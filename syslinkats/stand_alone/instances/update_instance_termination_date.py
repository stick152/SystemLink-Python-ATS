"""
update_instance_termination_date.py

This module allows a user to change the value of the TerminationDate tag for instances.
"""
__author__ = 'sedwards'

import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict

from syslinkats import ats_config_file
from syslinkats.framework.aws.aws_instance import AWSInstance
from syslinkats.framework.common.argparse_helpers import bool_from_str
from syslinkats.framework.file_io.json_file_operations import read_json_data_from_file
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.msteams.common.constants import (
    TEST_DAY_INSTANCE_WEBHOOK,
    DAILY_INSTANCES_WEBHOOK
)
from syslinkats.framework.msteams.msteams_operations import post_teams_instance_deployment_message

LOGGER = AutoIndent(stream=sys.stdout)
ATS_CONFIG_DATA: Dict[str, str] = {}


def parse_args() -> argparse.Namespace:
    """Returns options to the caller.

        This function parses out and returns arguments and options from the
        commandline arguments.

    Returns:
        argparse.Namespace: The parsed arguments for the script.
    """
    parser = argparse.ArgumentParser(
        description='Build the nipkg.ini file based on url specifications.'
    )

    parser.add_argument(
        '--ats-config-path', action='store', type=str, default=ats_config_file(),
        dest='ats_config_path',
        help='''This is the path to your local copy of the default_conf.json file.
            If you do not provide this path, then the default one (included in the ATS) will be
            used instead.'''
    )

    parser.add_argument(
        '-N', '--instance-dns-name', action='append', type=str, default=None,
        dest='instance_dns_names',
        help='''The public DNS name(s) of the instance(s) whose termination date needs updating.
        Please note that this is an appending list, so use -N <dns_name> -N <dns_name> for
        multiple instances.'''
    )

    parser.add_argument(
        '--instance-termination-date', action='store', type=str,
        default=str(datetime.today().date() + timedelta(days=2)),
        dest='instance_termination_date',
        help='''The date at which the instance can be terminated.  Format: %Y-%m-%d
        Note that this value will default to two days from today().'''
    )

    parser.add_argument(
        '--is-test-day-instance', action='store', default=False, type=bool_from_str,
        dest='is_test_day_instance',
        help='Whether or not this instance is for use in test days.'
    )

    return parser.parse_args()


def main():
    """The main execution method for the script."""
    args = parse_args()

    global ATS_CONFIG_DATA  # pylint: disable=global-statement
    ATS_CONFIG_DATA = read_json_data_from_file(args.ats_config_path)

    # Get the AWSInstance to use for instance operations.
    aws_instance = AWSInstance(region_name=ATS_CONFIG_DATA['region_name'])

    LOGGER.write(
        f'Updating the TerminationDate tag for instances: {args.instance_dns_names} to '
        f'{args.instance_termination_date}'
    )

    # Update (or create) the TerminationDate tag value.
    aws_instance.create_or_update_tag_value(
        resource_ids=aws_instance.public_dns_names_to_ids(args.instance_dns_names),
        tags=[{'Key': 'TerminationDate', 'Value': args.instance_termination_date}]
    )

    LOGGER.write('Tag operation complete.')
    # Post the message to the proper MSTeams channel.
    post_teams_instance_deployment_message(
        web_hook=TEST_DAY_INSTANCE_WEBHOOK if args.is_test_day_instance
        else DAILY_INSTANCES_WEBHOOK,
        card_title='SystemLink Daily Instance Update.' if not args.is_test_day_instance
        else 'SystemLink Test Day Instance Update',
        card_text=f'The termination date for the following instances has been updated to '
                  f'<b>{args.instance_termination_date}</b>:<br><br>' +
                  "<br>".join(args.instance_dns_names)
    )


if __name__ == '__main__':
    main()
