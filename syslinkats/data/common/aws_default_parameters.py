#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aws_default_parameters.py

This module holds default parameters and/or objects to be used by the AWS ATS.
"""
# Defaults to use when accessing services on the main AWS SysLink instance.
DEFAULT_AWS_SYSLINK_ACCESS_DATA = {
    'name': 'systemlink-jenkins.aws.natinst.com',
    'username': 'ni-systemlink-dev',
    'password': 'Kn1ghtR!der'
}

# Defaults to use when creating and/or accessing instances.
DEFAULT_SECURITY_GROUP_IDS = ['sg-02b4b7b6eefa0aea1', 'sg-0d0107dfbfda18fcb']
DEFAULT_INSTANCE_TAGS = [{'Key': 'Category', 'Value': 'ATSInstance'}]
DEFAULT_AMI_FILTERS = [{'Name': 'tag:Category', 'Values': ['BaseImage']}]
DEFAULT_IAM_INSTANCE_PROFILE = {'Name': 'ni-systemlink-ec2role-dev'}
DEFAULT_INSTANCE_KEY_NAME = 'Category'
DEFAULT_INSTANCE_KEY_VALUES = ['BaseInstance', 'ATSInstance']
DEFAULT_INSTANCE_TYPE = 'r5.xlarge'
DEFAULT_KEY_PAIR_NAME = 'syslink-jenkins'
DEFAULT_QUERY_INSTANCE_STATES = ['running']
DEFAULT_TAGS_TO_COPY = [
    'Category', 'CostCenter', 'Department', 'Feeds', 'SiteCode', 'Team', 'Tier']
DEFAULT_DIRECT_CONNECT_TAGS = [
    {'Key': 'CostCenter', 'Value': '2632'},
    {'Key': 'Department', 'Value': 'rd'},
    {'Key': 'SiteCode', 'Value': '001'},
    {'Key': 'Team', 'Value': 'systemlink-aws@ni.com'},
    {'Key': 'Tier', 'Value': 'dev'},
]
DEFAULT_AWS_REGION = 'us-east-1'
DEFAULT_SUBNET_ID = 'subnet-01e7368d67dc888c9'
DEFAULT_BLOCK_DEV_MAPPINGS = [{'DeviceName': '/dev/sda1', 'Ebs': {'DeleteOnTermination': True}}]

# Defaults to use for feed creation, removal, etc.
DEFAULT_MAJ_MIN_BUILD = '19.6.0'
