"""
provision_custom_instance.py

This module is responsible for the following:
* Deploy one or more instances.
* Install a specified build of SystemLink suite on to the instance.
* Add Windows users.
* Configure the NI Web Server.
* Configure user language preferences.
* Send a Teams notification upon completion with the following data:
    * Test Day or Daily Instance descriptor.
    * Who the instance was for (@mention?)
    * The URL to the instance.
    * The build of the SystemLink Suite that the feeds came from.
    * The feeds which were installed.
"""
__author__ = 'sedwards'

import argparse
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from syslinkats import (
    ats_config_file,
    installation_config_file,
    systemlink_server_config_file,
    user_config_file
)
from syslinkats.data.common.aws_default_parameters import (
    DEFAULT_AMI_FILTERS,
    DEFAULT_BLOCK_DEV_MAPPINGS,
    DEFAULT_DIRECT_CONNECT_TAGS,
    DEFAULT_IAM_INSTANCE_PROFILE,
    DEFAULT_INSTANCE_TYPE,
    DEFAULT_KEY_PAIR_NAME,
    DEFAULT_SECURITY_GROUP_IDS,
    DEFAULT_SUBNET_ID
)
from syslinkats.framework.aws.aws_image import AWSImage
from syslinkats.framework.aws.aws_instance import AWSInstance
from syslinkats.framework.common.argparse_helpers import bool_from_str, int_from_str
from syslinkats.framework.common.string_parse_helpers import parse_date_range
from syslinkats.framework.errors.custom_errors import FeedMissingError
from syslinkats.framework.file_io.json_file_operations import read_json_data_from_file
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.msteams.common.constants import (
    DAILY_INSTANCES_WEBHOOK,
    TEST_DAY_INSTANCE_WEBHOOK
)
from syslinkats.framework.msteams.msteams_operations import post_teams_instance_deployment_message
from syslinkats.framework.remote.remote_commands import run_aws_remote_command
from syslinkats.stand_alone.front_loaded_data.data_loader import call_uploaders
from syslinkats.tests.common.systemlink_server.systemlink_server_helpers import restart_web_server
from syslinkats.tests.setup.installation.utils.feed_utils import (
    add_feeds,
    get_feeds_to_install,
    install_feeds,
    remove_feeds,
    restart_instance,
    update_feeds,
    upgrade_package_manager,
    upgrade_updater_manager
)
from syslinkats.tests.setup.security.utils.security_helpers import (
    create_mappings_from_templates,
    create_users_from_templates,
    create_workspaces_from_templates,
    get_builtin_templates
)
from syslinkats.tests.setup.users.utils.user_helpers import (
    add_remote_windows_users,
    set_user_language_preferences
)

LOGGER = AutoIndent(stream=sys.stdout)
CREATED_INSTANCE_IDS: List[str] = []
PUBLIC_DNS_NAMES: List[str] = []
AWS_INSTANCE: AWSInstance
ATS_CONFIG_DATA: Dict[str, Any] = {}
SYSTEMLINK_SERVER_CONFIG_DATA: Dict[str, Any] = {}
USER_CONFIG_DATA: Dict[str, Any] = {}
INSTALLATION_CONFIG_DATA: Dict[str, Any] = {}
FEED_ITEMS: Optional[Tuple[str, List[Tuple[str, str]]]]


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
        '--installation-data-path', action='store', type=str,
        default=installation_config_file(), dest='installation_data_path',
        help='''This is the path to your local copy of the installation config.json file.
            If you do not provide this path, then the default one (included in the ATS) will be
            used instead.'''
    )

    parser.add_argument(
        '--systemlink-server-data-path', action='store', type=str,
        default=systemlink_server_config_file(), dest='systemlink_server_data_path',
        help='''This is the path to your local copy of the installation config.json file.
            If you do not provide this path, then the default one (included in the ATS) will be
            used instead.'''
    )

    parser.add_argument(
        '--user-data-path', action='store', type=str, default=user_config_file(),
        dest='user_data_path',
        help='''This is the path to your local copy of the user config.json file.
            If you do not provide this path, then the default one (included in the ATS) will be
            used instead.'''
    )

    parser.add_argument(
        '--use-dev-worker', action='store', type=bool_from_str, default=False,
        dest='use_dev_worker',
        help='''Tells the runners that you want to test using the syslink_worker_name
            specified in your copy of default_conf.json instead of creating new AWS ATS
            instances.'''
    )

    parser.add_argument(
        '--ami-id', action='store', type=str, default=None,
        dest='ami_id',
        help='The AMI id (if any) of the instance that you would like to deploy from.'
    )

    parser.add_argument(
        '--instance-count', action='store', type=int_from_str, default=1,
        dest='instance_count',
        help='The number of instance to create.',
    )

    parser.add_argument(
        '--instance-termination-date', action='store', type=str,
        default=str(datetime.today().date() + timedelta(days=2)),
        dest='instance_termination_date',
        help='The date at which the instance can be terminated.  Format: %Y-%m-%d'
    )

    parser.add_argument(
        '--maj-min-rev', action='store', default=None, type=str,
        dest='maj_min_rev',
        help='This is the major.minor.rev for the suite (i.e., 20.0.0)'
    )

    parser.add_argument(
        '--suite-date-range', action='store', default=None, type=str,
        dest='suite_date_range',
        help='''This can either be a string with a single date or a tuple string with a start
            and end date: i.e., "(01-15-2020, 01-30-2020)".
            Either way, the string date needs to be in the format %m-%d-%Y as that's how they're
            stored on the argohttp pages.'''
    )

    parser.add_argument(
        '--exact-build', action='store', default=None, type=str,
        dest='exact_build',
        help='''This is the exact build version (i.e., 20.0.0b25)'''
    )

    parser.add_argument(
        '-F', '--feeds-to-install', action='append', default=None, type=str,
        dest='feeds_to_install',
        help='''This is an appending list of feeds to install.  To use, simply add -F <feed
            name> for every feed to install (i.e., -F ni-systemlink-server -F
            ni-systemlink-client)'''
    )

    parser.add_argument(
        '--send-ms-teams-deployment-message', action='store', default=False, type=bool_from_str,
        dest='send_ms_teams_deployment_message',
        help='''If this value is True, then a message will be sent to the ASW SystemLink Daily
                Instances channel.'''
    )

    parser.add_argument(
        '--deployment-message-note', action='store', default=None, type=str,
        dest='deployment_message_note',
        help='''A special note to attach to the MS Teams notification card for this instance.
        This message will appear appended on to the report body text.'''
    )

    parser.add_argument(
        '--is-test-day-instance', action='store', default=False, type=bool_from_str,
        dest='is_test_day_instance',
        help='Whether or not this instance is for use in test days.'
    )

    parser.add_argument(
        '--front-load-data', action='store', default=True, type=bool_from_str,
        dest='front_load_data',
        help='Whether data should be front-loaded to this instance.'
    )

    return parser.parse_args()


def populate_global_data(args: argparse.Namespace) -> None:
    """Populate various global variables."""
    global ATS_CONFIG_DATA  # pylint: disable=global-statement
    global AWS_INSTANCE  # pylint: disable=global-statement
    global CREATED_INSTANCE_IDS  # pylint: disable=global-statement
    global PUBLIC_DNS_NAMES  # pylint: disable=global-statement
    global SYSTEMLINK_SERVER_CONFIG_DATA  # pylint: disable=global-statement
    global USER_CONFIG_DATA  # pylint: disable=global-statement
    global INSTALLATION_CONFIG_DATA  # pylint: disable=global-statement

    ATS_CONFIG_DATA = read_json_data_from_file(args.ats_config_path)
    AWS_INSTANCE = AWSInstance(region_name=ATS_CONFIG_DATA['region_name'])
    SYSTEMLINK_SERVER_CONFIG_DATA = read_json_data_from_file(args.systemlink_server_data_path)
    USER_CONFIG_DATA = read_json_data_from_file(args.user_data_path)
    INSTALLATION_CONFIG_DATA = read_json_data_from_file(args.installation_data_path)

    if args.use_dev_worker:
        # When the user specifies that they want to use the dev worker, then no instance will be
        # created.  This means that we'll need to fill in the PUBLIC_DNS_NAMES and
        # CREATED_INSTANCE_IDS from what's in the json conf file.
        PUBLIC_DNS_NAMES = [ATS_CONFIG_DATA['syslink_worker_name']]
        if not ATS_CONFIG_DATA['syslink_worker_instance_id']:
            CREATED_INSTANCE_IDS = AWS_INSTANCE.describe_instance_ids(
                filters=[
                    {
                        'Name': 'private-dns-name',
                        'Values': AWSInstance.public_dns_names_to_private(PUBLIC_DNS_NAMES)
                    }
                ]
            )
        else:
            CREATED_INSTANCE_IDS = [ATS_CONFIG_DATA['syslink_worker_instance_id']]


def deploy_base_instance(args: argparse.Namespace) -> None:
    """Deploys n-number of instances as specified in the command arguments."""
    global CREATED_INSTANCE_IDS  # pylint: disable=global-statement
    global PUBLIC_DNS_NAMES  # pylint: disable=global-statement

    LOGGER.write('Deploying base instance.')

    # If the user didn't specify an AMI Id to deploy from, then get the id of the base image.
    if not args.ami_id:
        with AWSImage(region_name=ATS_CONFIG_DATA['region_name']) as aws_image:
            ami_id = aws_image.describe_image_ids(
                filters=DEFAULT_AMI_FILTERS, owners=['self'], state=['available'])

    # Build the list of tags to add to the new instance.
    if args.is_test_day_instance:
        new_tags = [{'Key': 'Category', 'Value': 'TestDayInstance'}]
    else:
        new_tags = [{'Key': 'Category', 'Value': 'DailyInstance'}]
    new_tags.append({'Key': 'TerminationDate', 'Value': args.instance_termination_date.strip()})
    new_tags.extend(DEFAULT_DIRECT_CONNECT_TAGS)

    # Create the instance(s).
    CREATED_INSTANCE_IDS = AWS_INSTANCE.create_instances(
        ami_id=ami_id,
        block_device_mappings=DEFAULT_BLOCK_DEV_MAPPINGS,
        subnet_id=DEFAULT_SUBNET_ID,
        instance_type=DEFAULT_INSTANCE_TYPE,
        instance_count=args.instance_count,
        key_pair_name=DEFAULT_KEY_PAIR_NAME,
        security_group_ids=DEFAULT_SECURITY_GROUP_IDS,
        iam_instance_profile=DEFAULT_IAM_INSTANCE_PROFILE,
        new_tags=new_tags
    )
    LOGGER.write(f'Created instance Ids: {CREATED_INSTANCE_IDS}')

    # Get the public DNS name(s) of the instance(s) that you deployed.
    # NOTE: I had to refactor this into a loop as the internal AWS describe instance call was
    # re-ordering the list such that public DNS names were not matching the list of created
    # instance ids.  This *forces* it to be in the same order.
    for instance_id in CREATED_INSTANCE_IDS:
        private_dns_names = AWS_INSTANCE.describe_instance_dns_names(
            instance_ids=[instance_id], get_private_dns_name=True, newest_only=False)
        PUBLIC_DNS_NAMES.extend(AWS_INSTANCE.private_dns_names_to_public(
            private_dns_names=private_dns_names
        ))
    LOGGER.write(f'Public DNS Names: {PUBLIC_DNS_NAMES}')


def software_provisioning(args: argparse.Namespace) -> None:
    """Install feeds onto the specified instances.

    Notes:
        This function performs the following operations:
        - Scrapes argohttp for the appropriate suite to install and extracts its feeds (
        including its associated Package Manager feed).
        - Remove existing instances of the feeds to be installed.
        - Adds instances of the feeds to be installed to Package Manager.
        - Tells Package Manager to update the feeds.
        - Upgrades the Package Manager upgrader.
        - Upgrades Package Manager.
        - Installs the feeds.
        - Restarts the instance(s).
    """
    global FEED_ITEMS  # pylint: disable=global-statement

    LOGGER.write('Installing SystemLink software.')

    FEED_ITEMS = get_feeds_to_install(
        installation_config_data=INSTALLATION_CONFIG_DATA,
        maj_min_rev=args.maj_min_rev,
        date_range=parse_date_range(
            args.suite_date_range.strip()) if args.suite_date_range else None,
        exact_build=args.exact_build,
        feeds_to_install=args.feeds_to_install
    )

    # Output which feeds we'll be installing.
    LOGGER.write('The following feeds will be installed:')
    for feed_item in FEED_ITEMS:
        LOGGER.write(feed_item)

    LOGGER.write('Removing feeds...')
    remove_feeds(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA,
        feed_items=FEED_ITEMS
    )

    LOGGER.write('Adding feeds...')
    add_feeds(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA,
        feed_items=FEED_ITEMS
    )

    LOGGER.write('Updating all feeds.')
    update_feeds(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA
    )

    LOGGER.write('Upgrading Package Manager Updater.')
    package_manager_feed_item: Tuple[str, str]
    try:
        package_manager_feed_item = next(_ for _ in FEED_ITEMS[1] if 'package-manager' in _[0])
    except StopIteration:
        raise FeedMissingError(
            'The package-manager feed item was missing from the list of feed items.')

    upgrade_updater_manager(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA,
        package_manager_feed_item=package_manager_feed_item
    )

    LOGGER.write('Upgrading Package Manager.')
    upgrade_package_manager(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA
    )

    LOGGER.write('Installing feeds...')
    install_feeds(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        installation_config_data=INSTALLATION_CONFIG_DATA,
        feed_items=FEED_ITEMS
    )

    LOGGER.write('Restarting instance...')
    restart_instance(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_public_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS
    )


def add_windows_users() -> None:
    """Adds windows users to the remote instance(s)."""
    LOGGER.write('Adding Windows users.')

    add_remote_windows_users(
        region_name=ATS_CONFIG_DATA['region_name'],
        target_dns_names=PUBLIC_DNS_NAMES,
        instance_ids=CREATED_INSTANCE_IDS,
        user_config_data=USER_CONFIG_DATA
    )


def configure_ni_web_server() -> None:
    """Configures the NI Web Server on all created instances."""
    LOGGER.write('Configuring the NI Web Server.')

    # For each instance, run the NI Web Server configuration command.
    for public_dns_name, instance_id in zip(PUBLIC_DNS_NAMES, CREATED_INSTANCE_IDS):
        run_aws_remote_command(
            region_name=ATS_CONFIG_DATA['region_name'],
            target_public_dns_names=[public_dns_name],
            instance_ids=[instance_id],
            remote_command=SYSTEMLINK_SERVER_CONFIG_DATA['ni_web_server_config_command'].format(
                public_dns_name
            ),
            output_ignore_list=SYSTEMLINK_SERVER_CONFIG_DATA['output_ignore_list'],
            total_command_run_time=300
        )


def configure_user_language_preferences() -> None:
    """Configures the users' language preferences on all created instances."""
    LOGGER.write('Configuring user language preferences.')

    set_user_language_preferences(
        http_prefix=ATS_CONFIG_DATA['http_prefix'],
        target_dns_names=PUBLIC_DNS_NAMES,
        target_system_username=ATS_CONFIG_DATA['syslink_worker_system_username'],
        target_system_password=ATS_CONFIG_DATA['syslink_worker_system_password'],
        user_config_data=USER_CONFIG_DATA
    )


def set_security_defaults() -> None:
    """Set up default workspaces, users and mappings based on built-in templates."""
    for public_dns_name in PUBLIC_DNS_NAMES:
        ATS_CONFIG_DATA['syslink_worker_name'] = public_dns_name

        templates = get_builtin_templates(ats_config_data=ATS_CONFIG_DATA)
        workspaces = create_workspaces_from_templates(
            templates=templates, ats_config_data=ATS_CONFIG_DATA)
        users = create_users_from_templates(templates=templates, ats_config_data=ATS_CONFIG_DATA)
        create_mappings_from_templates(
            templates=templates,
            workspaces=workspaces,
            users=users,
            ats_config_data=ATS_CONFIG_DATA
        )


def send_teams_notification(args: argparse.Namespace) -> None:
    """Send an MS Teams notification that the instance was created and configured."""
    LOGGER.write('Sending an MS Teams notification.')

    # Create the full https URL to the instances.
    instance_urls = AWSInstance.get_formatted_instance_urls(
        http_prefix=ATS_CONFIG_DATA['http_prefix'], dns_names=PUBLIC_DNS_NAMES)

    # Post the message to the proper MSTeams channel.
    card_text = f'This instance will expire on <b>{args.instance_termination_date}</b>'
    if args.deployment_message_note:
        card_text += f'Special Note:<br><br>{args.deployment_message_note}'
    post_teams_instance_deployment_message(
        web_hook=TEST_DAY_INSTANCE_WEBHOOK if args.is_test_day_instance
        else DAILY_INSTANCES_WEBHOOK,
        card_title='SystemLink Daily Instance Report.' if not args.is_test_day_instance
        else 'SystemLink Test Day Instance Report',
        card_text=card_text,
        instance_urls_section_title='<b>Instance URLs</b>',
        instance_urls_section_text='The following instances were created for daily use:' if not
        args.is_test_day_instance
        else 'The following instances were created for Test Day use:',
        instance_urls=instance_urls,
        install_section_title='<b>Installations</b>',
        install_section_text='The following suite and feeds were installed:',
        suite_build=FEED_ITEMS[0],
        feeds_list=FEED_ITEMS[1]
    )


if __name__ == '__main__':
    ARGS = parse_args()

    # Fill in any necessary globals.
    populate_global_data(ARGS)

    # Deploy a base instance.
    if not ARGS.use_dev_worker:
        deploy_base_instance(ARGS)

    # Install SW.
    software_provisioning(ARGS)

    # Add Windows users.
    add_windows_users()

    # Configure the NI Web Server.
    configure_ni_web_server()

    # Configure user language preferences.
    configure_user_language_preferences()

    # Set up the workspaces, users and mappings for each built-in template.
    set_security_defaults()

    # Restart the web server.
    for public_dns_name_, instance_id_ in zip(PUBLIC_DNS_NAMES, CREATED_INSTANCE_IDS):
        ATS_CONFIG_DATA['syslink_worker_name'] = public_dns_name_
        ATS_CONFIG_DATA['syslink_worker_instance_id'] = instance_id_
        restart_web_server(ats_config_data=ATS_CONFIG_DATA)

    # Front-load data to the instances.
    if ARGS.front_load_data:
        for public_dns_name_ in PUBLIC_DNS_NAMES:
            ATS_CONFIG_DATA['syslink_worker_name'] = public_dns_name_
            call_uploaders(ATS_CONFIG_DATA)

    # Send a Teams notification.
    send_teams_notification(ARGS)
