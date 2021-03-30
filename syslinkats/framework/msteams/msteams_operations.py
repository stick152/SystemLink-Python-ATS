"""
msteams_operations.py

This module contains functions for sending notifications to the SystemLink MSTeams channels.
"""
import pymsteams

from syslinkats.framework.msteams.common.constants import (
    GENERAL_FAILURE_WEBHOOK
)
from syslinkats.framework.validators.validate_args import validate_args_for_value


# pylint: disable=too-many-locals
def post_teams_instance_deployment_message(**kwargs):
    """Post the Daily Instance message to the appropriate MSTeams channel."""

    # Extract the arguments.
    web_hook = kwargs.pop('web_hook', None)
    card_title = kwargs.pop('card_title', None)
    card_text = kwargs.pop('card_text', None)
    instance_urls_section_title = kwargs.pop('instance_urls_section_title', None)
    instance_urls_section_text = kwargs.pop('instance_urls_section_text', None)
    instance_urls = kwargs.pop('instance_urls', None)
    install_section_title = kwargs.pop('install_section_title', None)
    install_section_text = kwargs.pop('install_section_text', None)
    suite_build = kwargs.pop('suite_build', None)
    feeds_list = kwargs.pop('feeds_list', None)

    # You must create the connector card object with the Microsoft Web hook URL.
    connector_card = pymsteams.connectorcard(web_hook)

    # Add a title.
    if card_title:
        connector_card.title(card_title)

    # # Add text to the message.
    if card_text:
        connector_card.text(card_text)

    # Add a link to the instance's URL.
    if instance_urls:
        instance_urls_section = pymsteams.cardsection()
        instance_urls_section.enableMarkdown()
        instance_urls_section.title(instance_urls_section_title)

        if instance_urls_section_text:
            instance_urls_section.text(instance_urls_section_text)

        for instance_url in instance_urls:
            instance_urls_section.addFact('', '[{0}]({0})'.format(instance_url))

        # Add this section to the card.
        connector_card.addSection(instance_urls_section)

    # Add an installed feeds section.
    if install_section_title:
        install_activity_section = pymsteams.cardsection()
        install_activity_section.enableMarkdown()
        install_activity_section.title(install_section_title)

        # Add text to the section.
        if install_section_text:
            install_activity_section.text(install_section_text)

        # Add the path to the suite .iso used for creating feeds.
        if suite_build:
            install_activity_section.addFact('Suite Build', suite_build)

        # Add the list of packages (including versions) which were used to create the feeds.
        if feeds_list:
            for feed in feeds_list:
                install_activity_section.addFact('*', feed[0])

        # Add this section to the card.
        connector_card.addSection(install_activity_section)

    # send the message.
    connector_card.send()


def post_teams_test_failure_notice(**kwargs):
    """Post test failures to the appropriate MSTeams squad."""
    # Extract the arguments.
    web_hook = kwargs.pop('web_hook', GENERAL_FAILURE_WEBHOOK)
    card_title = kwargs.pop('card_title', None)
    card_text = kwargs.pop('card_text', None)
    bucket_test_data = kwargs.pop('bucket_test_data', None)

    # Validate specific args that must have a value.  Note that we don't need to worry about
    # card_text as it's not generally required.
    validate_args_for_value(card_title=card_title, bucket_test_data=bucket_test_data)

    # You must create the connector card object with the Microsoft Web hook URL.
    connector_card = pymsteams.connectorcard(web_hook)

    # Add a title.
    connector_card.title(card_title)

    # Add text to the message.
    if card_text:
        connector_card.text(card_text)

    # Add a list of squad owners (if available).
    if bucket_test_data['squad_owners']:
        squad_section = pymsteams.cardsection()
        squad_section.title('Squad Owners')
        squad_section.disableMarkdown()

        for squad_owner in bucket_test_data['squad_owners']:
            squad_section.addFact('Squad Owner', squad_owner)

        # Add this section to the card.
        connector_card.addSection(squad_section)

    # Add a list of test issues (if available).
    if bucket_test_data['tests']:
        issues_section = pymsteams.cardsection()
        issues_section.title('Issues')
        issues_section.disableMarkdown()

        for bucket_test_issue in bucket_test_data['tests']:
            for test_issue in bucket_test_issue.items():
                key, value = test_issue
                issues_section.addFact(key, value)

        # Add this section to the card.
        connector_card.addSection(issues_section)

    # send the message.
    connector_card.send()
