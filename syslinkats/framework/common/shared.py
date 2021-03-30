#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
shared.py
"""
import os

__author__ = 'sedwards'

# this could be 'http' for testing locally
HTTP_PREFIX = 'https'

# This is for debug or single-master testing purposes.
MASTER_DATA = dict(
    context_id='ats-default',
    name='ec2-18-223-238-27.us-east-2.compute.amazonaws.com',
    username='admin',
    password='labview===',
    # skyline_username='admin',
    # skyline_password='labview===',
    amqp_username='niskyline',
    amqp_password='',
    test_user1_name='test_user1',
    test_user1_password='password1',
    test_user2_name='test_user2',
    test_user2_password='password2'
)
