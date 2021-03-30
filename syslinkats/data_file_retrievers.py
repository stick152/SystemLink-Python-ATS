"""
data_file_retrievers.py

This module contains methods for retrieving paths to all configuration .json files.
"""
import pkg_resources


def ats_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/default_conf.json')


def installation_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/installation/data/config.json')


def instance_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/instances/data/config.json')


def systemlink_server_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/systemlink_server/data/config.json')


def user_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/users/data/config.json')


def workspaces_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/workspaces/data/config.json')


def security_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/security/data/config.json'
    )

def mongo_config_file():
    return pkg_resources.resource_filename(
        'syslinkats', 'tests/setup/mongo/data/config.json')
