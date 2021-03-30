"""
manual_instance_termination.py
"""
import argparse
import ast
import os
import sys

from syslinkats.framework.aws.aws_instance import AWSInstance
from syslinkats.framework.logging.auto_indent import AutoIndent

LOGGER = AutoIndent(sys.stdout)


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
        '-N', '--instance-dns-name', action='append', type=str, default=None,
        dest='instance_dns_names',
        help='''The public DNS name(s) of the instance(s) whose termination date needs updating.
        Please note that this is an appending list, so use -N <dns_name> -N <dns_name> for
        multiple instances.'''
    )

    return parser.parse_args()


def main(args: argparse.Namespace):
    if args.instance_dns_names:
        aws_instance = AWSInstance(region_name='us-east-1')
        try:
            _instance_dns_names = ast.literal_eval(args.instance_dns_names)
        except ValueError:
            # This can happen if the arg is just a normal string or is a malformed object.
            # If so, just return the arg as-is.
            _instance_dns_names = args.instance_dns_names

        if _instance_dns_names:
            if isinstance(_instance_dns_names, str):
                instance_ids = aws_instance.public_dns_names_to_ids([_instance_dns_names])
            else:
                instance_ids = aws_instance.public_dns_names_to_ids(_instance_dns_names)

            if instance_ids:
                aws_instance.cleanup_instances(instance_ids=instance_ids, do_terminate=True)
            else:
                LOGGER.write(
                    f'No instance Ids were found for the specified DNS names: '
                    f'{_instance_dns_names}')
    else:
        LOGGER.write('No instance DNS name was provided, so there is nothing to do.')


if __name__ == '__main__':
    _args = parse_args()
    main(_args)
