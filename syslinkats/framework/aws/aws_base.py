#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aws_base.py
"""
import abc
import argparse
import datetime
from typing import Optional
from typing import Tuple
from typing import Union

import boto3


class AWSHTTPStatusError(Exception):
    def __init__(self, message):
        self.message = message


class AWSBase(metaclass=abc.ABCMeta):
    """"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.ec2_client = boto3.client('ec2', **kwargs)
        self.ec2_resource = boto3.resource('ec2', **kwargs)
        self.ssm_client = boto3.client('ssm', **kwargs)

    @staticmethod
    def _parse_date_range(date_range: Tuple[datetime.date, Union[datetime.date, None]] = None) \
            -> Tuple[datetime.date, Optional[datetime.date]]:
        """

        Args:
            date_range:

        Returns:

        """
        if date_range is None:
            raise TypeError('You must provide a valid date argument.')

        end_date = None
        if date_range is not None and type(date_range) is tuple:
            if len(date_range) == 0:
                raise TypeError('Invalid date_range tuple.')

            if type(date_range[0]) is datetime.date:
                start_date = date_range[0]
            else:
                raise TypeError('Invalid date_range tuple.')

            if len(date_range) > 1:
                if type(date_range[1]) is datetime.date:
                    end_date = date_range[1]
                elif date_range[1] is not None:
                    raise TypeError('Invalid date_range tuple.')
        else:
            raise TypeError('Invalid date_range type.')

        return start_date, end_date

    @staticmethod
    def _validate_response_status(response: dict = None, expected_status: int = 200) -> None:
        """

        Args:
            response:
            expected_status:

        Returns:

        """
        http_status = response['ResponseMetadata']['HTTPStatusCode']
        if http_status != expected_status:
            raise AWSHTTPStatusError('Expected a {} status, but received {}'.format(
                expected_status, http_status))

    @staticmethod
    def validate_command_args(args: argparse.Namespace = None):
        """

        Args:
            args:

        Returns:

        """
        import ast
        from syslinkats.data.common.aws_default_parameters import DEFAULT_AMI_FILTERS
        from syslinkats.data.common.aws_default_parameters import DEFAULT_AWS_REGION
        from syslinkats.data.common.aws_default_parameters import DEFAULT_AWS_SYSLINK_ACCESS_DATA
        from syslinkats.data.common.aws_default_parameters import DEFAULT_BLOCK_DEV_MAPPINGS
        from syslinkats.data.common.aws_default_parameters import DEFAULT_IAM_INSTANCE_PROFILE
        from syslinkats.data.common.aws_default_parameters import DEFAULT_INSTANCE_KEY_NAME
        from syslinkats.data.common.aws_default_parameters import DEFAULT_INSTANCE_KEY_VALUES
        from syslinkats.data.common.aws_default_parameters import DEFAULT_INSTANCE_TYPE
        from syslinkats.data.common.aws_default_parameters import DEFAULT_INSTANCE_TAGS
        from syslinkats.data.common.aws_default_parameters import DEFAULT_KEY_PAIR_NAME
        from syslinkats.data.common.aws_default_parameters import DEFAULT_MAJ_MIN_BUILD
        from syslinkats.data.common.aws_default_parameters import DEFAULT_QUERY_INSTANCE_STATES
        from syslinkats.data.common.aws_default_parameters import DEFAULT_SECURITY_GROUP_IDS
        from syslinkats.data.common.aws_default_parameters import DEFAULT_SUBNET_ID
        from syslinkats.data.common.aws_default_parameters import DEFAULT_TAGS_TO_COPY

        # If the user omitted the region_name arg or passed in an empty string
        # then use the default string.
        if hasattr(args, 'region_name') and \
                (args.region_name is None or len(args.region_name) == 0):
            args.region_name = DEFAULT_AWS_REGION

        # If the user omitted the subnet_id arg or passed in an empty string
        # then use the default string.
        if hasattr(args, 'subnet_id') and \
                (args.subnet_id is None or len(args.subnet_id) == 0):
            args.subnet_id = DEFAULT_SUBNET_ID

        # If the user omitted the instance_key_name arg or passed in an empty string
        # then use the default string.
        if hasattr(args, 'instance_key_name') and \
                (args.instance_key_name is None or args.instance_key_name == ''):
            args.instance_key_name = DEFAULT_INSTANCE_KEY_NAME

        # If the user omitted the instance_key_values arg or passed in an empty string
        # then use the default list.
        if hasattr(args, 'instance_key_values') and \
                (args.instance_key_values is None or len(args.instance_key_values) == 0):
            args.instance_key_values = DEFAULT_INSTANCE_KEY_VALUES
        if hasattr(args, 'instance_key_values') and type(args.instance_key_values) is str:
            args.instance_key_values = ast.literal_eval(args.instance_key_values)

        # If the user omitted the region_name arg or passed in an empty string
        # then use the default string.
        if hasattr(args, 'key_pair_name') and \
                (args.key_pair_name is None or args.key_pair_name == ''):
            args.key_pair_name = DEFAULT_KEY_PAIR_NAME

        # If the user omitted the tags_to_copy arg or passed in an empty string
        # then use the default list.
        if hasattr(args, 'tags_to_copy') and \
                (args.tags_to_copy is None or len(args.tags_to_copy) == 0):
            args.tags_to_copy = DEFAULT_TAGS_TO_COPY
        elif hasattr(args, 'tags_to_copy') and type(args.tags_to_copy) is str:
            args.tags_to_copy = ast.literal_eval(args.tags_to_copy)

        # If the user included the tags_to_create arg, then evaluate it.
        if hasattr(args, 'tags_to_create') and \
                (args.tags_to_create is not None and len(args.tags_to_create) > 0):
            args.tags_to_create = [ast.literal_eval(_) for _ in args.tags_to_create]

        # If the user omitted the query_instance_states arg or passed in an empty string
        # then use the default list.
        if hasattr(args, 'query_instance_states') and \
                (args.query_instance_states is None or len(args.query_instance_states) == 0):
            args.query_instance_states = DEFAULT_QUERY_INSTANCE_STATES
        elif hasattr(args, 'query_instance_states') and type(args.query_instance_states) is str:
            args.query_instance_states = ast.literal_eval(args.query_instance_states)

        # If the user omitted the testmon_server_data arg or passed in an empty string
        # then use the default dict.  Otherwise, eval the string to a dict.
        if hasattr(args, 'testmon_server_data') and \
                (args.testmon_server_data is None or len(args.testmon_server_data) == 0):
            args.testmon_server_data = DEFAULT_AWS_SYSLINK_ACCESS_DATA
        elif hasattr(args, 'testmon_server_data') and type(args.testmon_server_data) is str:
            args.testmon_server_data = ast.literal_eval(args.testmon_server_data)

        # If the user omitted the repo_server_data arg or passed in an empty string (Jenkins does
        # this), then use the default dict.  Otherwise, eval the string to a dict.
        if hasattr(args, 'repo_server_data') and \
                (args.repo_server_data is None or len(args.repo_server_data) == 0):
            args.repo_server_data = DEFAULT_AWS_SYSLINK_ACCESS_DATA
        elif hasattr(args, 'repo_server_data') and type(args.repo_server_data) is str:
            args.repo_server_data = ast.literal_eval(args.repo_server_data)

        # If the user omitted the iam_instance_profile, use the default.
        if hasattr(args, 'iam_instance_profile') and \
                (args.iam_instance_profile is None or len(args.iam_instance_profile) == 0):
            args.iam_instance_profile = DEFAULT_IAM_INSTANCE_PROFILE
        elif hasattr(args, 'iam_instance_profile') and type(args.iam_instance_profile) is str:
            args.iam_instance_profile = ast.literal_eval(args.iam_instance_profile)

        # If the user omitted the security_group_ids, use the default.
        if hasattr(args, 'security_group_ids') and \
                (args.security_group_ids is None or len(args.security_group_ids) == 0):
            args.security_group_ids = DEFAULT_SECURITY_GROUP_IDS

        if hasattr(args, 'block_device_mappings') and \
                (args.block_device_mappings is None or len(args.block_device_mappings) == 0):
            args.block_device_mappings = DEFAULT_BLOCK_DEV_MAPPINGS
        elif hasattr(args, 'block_device_mappings') and type(args.block_device_mappings) is list:
            args.block_device_mappings = [ast.literal_eval(_) for _ in args.block_device_mappings]

        # If the user omitted the instance_tags, use the default list of dicts.  Otherwise,
        # eval the string to a list of dicts.
        if hasattr(args, 'instance_tags') and \
                (args.instance_tags is None or len(args.instance_tags) == 0):
            args.instance_tags = DEFAULT_INSTANCE_TAGS
        elif hasattr(args, 'instance_tags') and type(args.instance_tags) is list:
            args.instance_tags = [ast.literal_eval(_) for _ in args.instance_tags]

        # If the user included a valid image_name_desc arg, then evaluate it.
        if hasattr(args, 'image_name_desc') and \
                (args.image_name_desc is not None and len(args.image_name_desc) > 0):
            args.image_name_desc = [ast.literal_eval(_) for _ in args.image_name_desc]

        # If the user omitted the instance_type arg or passed in an empty string
        # then use the default string.
        if hasattr(args, 'instance_type') and \
                (args.instance_type is None or len(args.instance_type) == 0):
            args.instance_type = DEFAULT_INSTANCE_TYPE

        # If the user omitted the maj_min_build arg or passed in an empty string
        # then use the default.
        if hasattr(args, 'maj_min_build') and \
                (args.maj_min_build is None or len(args.maj_min_build) == 0):
            args.maj_min_build = DEFAULT_MAJ_MIN_BUILD

        # Ensure that we get a valid AMI Id.  Default here is to get the newest
        # AMI with Category==BaseImage.
        if hasattr(args, 'ami_id') and (args.ami_id is None or len(args.ami_id) == 0):
            from syslinkats.framework.aws.aws_image import AWSImage
            with AWSImage(region_name=args.region_name) as aws_image:
                ami_filters = None
                if hasattr(args, 'ami_filters') and \
                        (args.ami_filters is None or len(args.ami_filters) == 0):
                    args.ami_filters = DEFAULT_AMI_FILTERS
                    ami_filters = args.ami_filters
                elif hasattr(args, 'ami_filters') and type(args.ami_filters) is list:
                    args.ami_filters = [ast.literal_eval(_) for _ in args.ami_filters]
                    ami_filters = args.ami_filters

                ami_id = aws_image.describe_image_ids(
                    filters=ami_filters, owners=['self'], state=['available'])
                if ami_id is None:
                    raise ValueError(
                        'Unable to find a valid AMI with a matching filters: {}'.format(
                            args.ami_filters))
                else:
                    args.ami_id = ami_id
