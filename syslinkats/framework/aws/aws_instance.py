"""
aws_instance.py
"""
__author__ = 'sedwards'

import socket
import sys
import time
import uuid
from datetime import timedelta, datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from botocore.exceptions import ClientError
from dateutil.tz import tzutc

from syslinkats.data.common.aws_default_parameters import DEFAULT_QUERY_INSTANCE_STATES
from syslinkats.framework.aws import AWSBase
from syslinkats.framework.logging.auto_indent import AutoIndent

# Set up AutoIndent for logging.
from syslinkats.framework.validators.validate_args import validate_args_for_value

LOGGER = AutoIndent(stream=sys.stdout)


class AWSInstance(AWSBase):
    """A class for AWS Instance operations."""

    def __enter__(self):
        """This allows this class to be called using the 'with' keyword.
        For example:
            with <DerivedClassName>() as <short_name>:
                ...
        """
        # NOTE: Do any special stuff here.
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """This is called after scope is lost when the class is called using
        the 'with' keyword.

        NOTES:
        * In order to be called, all 4 positional args must be present.
        * Do any cleanup or disconnecting here.
        * Handle any exceptions here (optional).
        """

    def reset_session(self, **kwargs):
        """Reset the session by a re-init."""
        super().__init__(**kwargs)

    @classmethod
    def get_formatted_instance_urls(cls, http_prefix: str, dns_names: List[str]) -> List[str]:
        """A helper for formatting a list of URLs to the SystemLink server landing page for each
        instance.

        Args:
            http_prefix (str): The http prefix to use for the URLs (http, https).
            dns_names (List[str]): A list of public DNS names to use to build the URLs.

        Returns:
            List[str]: A list of instance URLs.
        """
        instance_urls_ = [f'{http_prefix}://{x}' for x in dns_names]
        return instance_urls_

    @classmethod
    def public_dns_names_to_private(cls, public_dns_names: Optional[List[str]],
                                    public_dns_suffix: str = 'aws.natinst.com') -> List[str]:
        """Replaces the public suffix for AWS instances (defaults to aws.natinst.com) with the
        private DNS suffix 'ec2.internal'.

        Args:
            public_dns_names (Optional[List[str]]): The public DNS names for the AWS instances.
            public_dns_suffix (str): The suffix for the public DNS name (defaults to
            aws.natinst.com).

        Returns:
            str: The name of the system with the ec2.internal suffix.
        """
        validate_args_for_value(public_dns_names=public_dns_names)
        private_dns_names: List[str] = []
        for public_dns_name in public_dns_names:
            private_dns_names.append(public_dns_name.replace(public_dns_suffix, 'ec2.internal'))
        return private_dns_names

    @classmethod
    def private_dns_names_to_public(cls, private_dns_names: Optional[List[str]],
                                    public_dns_suffix: str = 'aws.natinst.com') -> List[str]:
        """Replaces the private suffix for AWS instances (hard-coded to ec2.internal) with the
        public DNS suffix (defaults to 'aws.natinst.com').

        Args:
            private_dns_names (Optional[List[str]]): The private DNS names for the AWS instances.
            public_dns_suffix (str): The suffix for the public DNS name (defaults to
            aws.natinst.com).

        Returns:
            str: The name of the system with the provided public suffix.
        """
        validate_args_for_value(private_dns_names=private_dns_names)
        public_dns_names: List[str] = []
        for private_dns_name in private_dns_names:
            public_dns_names.append(private_dns_name.replace('ec2.internal', public_dns_suffix))
        return public_dns_names

    @staticmethod
    def _get_instances_value(reservation: dict = None) -> List[dict]:
        """

        Args:
            reservation:

        Returns:

        """
        if reservation is not None and isinstance(
                reservation, dict) and 'Instances' in reservation:
            return reservation['Instances']

        raise TypeError('The provided reservation must be a valid reservation dict.')

    @staticmethod
    def _get_instance_days_age(instance: dict = None) -> int:
        """

        Args:
            instance:

        Returns:

        """
        if instance is not None and isinstance(instance, dict):
            return (datetime.now(tz=tzutc()).date() -
                    AWSInstance._get_launch_date_value(instance)).days

        raise TypeError('The provided instance must be a valid instance dict.')

    @staticmethod
    def _get_launch_date_value(instance: dict = None) -> datetime.date:
        """

        Args:
            instance:

        Returns:

        """
        if instance is not None and isinstance(instance, dict):
            return AWSInstance._get_launch_time_value(instance).date()

        raise TypeError('The provided instance must be a valid instance dict.')

    @staticmethod
    def _get_launch_time_value(instance: dict = None) -> datetime:
        """

        Args:
            instance:

        Returns:

        """
        if instance is not None and isinstance(instance, dict) and 'LaunchTime' in instance:
            return instance['LaunchTime']

        raise TypeError('The provided instance must be a valid instance dict.')

    @staticmethod
    def _get_newest_instance(instances: List[dict] = None) -> dict:
        """

        Args:
            instances:

        Returns:

        """
        if instances is not None and len(instances) > 0:
            newest_instance = None
            today = datetime.today().date()
            for instance in instances:
                launch_date = AWSInstance._get_launch_date_value(instance)
                if newest_instance is None:
                    newest_instance = instance
                else:
                    if (today - launch_date).days < \
                            AWSInstance._get_instance_days_age(newest_instance):
                        newest_instance = instance
            return newest_instance

        raise TypeError('The provided instance must be a valid instance dict.')

    @staticmethod
    def _get_reservations_value(response: dict = None) -> list:
        """

        Args:
            response:

        Returns:

        """
        if response is not None and isinstance(response, dict) and 'Reservations' in response:
            return response['Reservations']

        raise TypeError('The provided response object must be a valid response dict.')

    @staticmethod
    def _get_state_name_value(instance: dict = None) -> str:
        """

        Args:
            instance:

        Returns:

        """
        if instance is not None and isinstance(instance, dict) and 'State' in instance \
                and 'Name' in instance['State']:
            return instance['State']['Name']

        raise TypeError('The provided instance must be a valid instance dict.')

    @staticmethod
    def wait_for_socket_on_instance(dns_name: str = None, port: int = 3389,
                                    retries: int = 10) -> None:
        """Wait for a socket to become available on a system at the specified DNS address.

        Args:
            dns_name:
            port:
            retries:

        Returns:
            None

        Raises:
            ConnectionError
        """
        for retry_count in range(retries):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((dns_name, 3389))
            sock.close()
            if result == 0:
                print("Port is open, continuing...")
                break

            print("Port is not open, retrying...")
            time.sleep(5)

            if retry_count >= retries - 1:
                raise ConnectionError(
                    'Retries exceeded.  Unable to connect to the specified port: {}.'.format(
                        port
                    ))

    # pylint: disable=too-many-arguments
    def cleanup_instances(self, instance_ids: List[str] = None,
                          filters: List[Dict[str, Union[str, List[str]]]] = None,
                          date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                          state: List[str] = None, do_terminate: bool = False,
                          do_wait: bool = True) -> List[str]:
        """

        Args:
            filters:
            instance_ids:
            date_range:
            state:
            do_terminate:
            do_wait:

        Returns:

        """
        instance_objects = self.get_instance_objects(
            instance_ids=instance_ids, filters=filters, date_range=date_range, state=state,
            newest_only=False)

        if len(instance_objects) == 0:
            LOGGER.write('No matching instance objects were found for cleanup.')
            return []

        _instance_ids = []
        for instance_object in instance_objects:
            LOGGER.write(
                f'Instance {instance_object.instance_id} will be '
                f'{"terminated" if do_terminate else "stopped"}.'
            )
            _instance_ids.append(instance_object.instance_id)
            if do_terminate:
                instance_object.terminate()
            else:
                instance_object.stop()

        if do_wait:
            LOGGER.write(
                'Waiting for instances to {}.'.format('terminate' if do_terminate else 'stop'))
            if do_terminate:
                waiter = self.ec2_client.get_waiter('instance_terminated')
            else:
                waiter = self.ec2_client.get_waiter('instance_stopped')

            waiter.wait(InstanceIds=_instance_ids, WaiterConfig={'Delay': 30, 'MaxAttempts': 999})
            LOGGER.write('Instance operations completed.')

        return _instance_ids

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    def create_images(self, instance_objects: List[Any] = None, instance_ids: List[str] = None,
                      filters: List[Dict[str, Union[str, List[str]]]] = None,
                      date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                      state: List[str] = None,
                      image_name_desc: List[Dict[str, str]] = None,
                      tags_to_copy: List[str] = None,
                      tags_to_create: List[dict] = None,
                      do_wait: bool = True, return_only_ids=True,
                      **kwargs) -> Union[List[Any], List[str]]:
        """

        Args:
            instance_objects:
            instance_ids:
            filters:
            date_range:
            state:
            image_name_desc:
            tags_to_copy:
            tags_to_create:
            do_wait:
            return_only_ids:
            **kwargs:

        Returns:

        """
        _instance_objects = []
        if instance_objects is not None and len(instance_objects) > 0:
            _instance_objects = instance_objects
        elif instance_ids is not None and len(instance_ids) > 0:
            _instance_objects = self.get_instance_objects(
                instance_ids=instance_ids, newest_only=False)
        elif (filters is not None and len(filters) > 0) \
                or (date_range is not None and len(date_range) > 0):
            _instance_objects = self.get_instance_objects(
                filters=filters, date_range=date_range, state=state, newest_only=False)

        created_images = []
        created_image_ids = []
        for i, instance_object in enumerate(_instance_objects):
            if image_name_desc is not None and len(image_name_desc) > i \
                    and 'Name' in image_name_desc[i]:
                if len(image_name_desc[i]['Name']) > 0:
                    name = image_name_desc[i]['Name'] + '_' + str(uuid.uuid4())
                else:
                    name = 'auto-gen-' + str(uuid.uuid4())

                if 'Description' in image_name_desc[i] \
                        and len(image_name_desc[i]['Description']) > 0:
                    description = image_name_desc[i]['Description']
                else:
                    description = ''
            else:
                name = 'auto-gen-' + str(uuid.uuid4())
                description = ''

            created_image = instance_object.create_image(
                Name=name, Description=description, **kwargs)
            created_images.append(created_image)
            created_image_ids.append(created_image.image_id)

            if tags_to_copy is not None and len(tags_to_copy) > 0:
                tag_objects = [_ for _ in instance_object.tags if _['Key'] in tags_to_copy]
                if tag_objects is not None and len(tag_objects) > 0:
                    created_image.create_tags(Tags=tag_objects)

            if tags_to_create is not None and len(tags_to_create) > 0:
                created_image.create_tags(Tags=tags_to_create)

        if do_wait and len(_instance_objects) > 0:
            LOGGER.write('AMIs being created: ' + ', '.join(created_image_ids))
            LOGGER.write('Sleeping for a bit so the waiter sees the target instances.')
            time.sleep(10)
            LOGGER.write('Waiting for images to become available.')
            waiter = self.ec2_client.get_waiter('image_available')
            waiter.wait(ImageIds=created_image_ids, WaiterConfig={'Delay': 30, 'MaxAttempts': 999})
            LOGGER.write('Images available.')

        if return_only_ids:
            return created_image_ids

        return created_images

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def create_instances(self, ami_id: str = None,
                         block_device_mappings: List[Dict[str, str]] = None,
                         subnet_id: str = None,
                         instance_type: str = None,
                         instance_count: int = 1,
                         key_pair_name: str = None, security_group_ids: List[str] = None,
                         iam_instance_profile: Dict[str, str] = None,
                         new_tags: List[Dict[str, str]] = None,
                         do_wait: bool = True,
                         return_only_ids: bool = True, **kwargs) -> Union[List[Any], List[str]]:
        """

        Args:
            ami_id:
            block_device_mappings:
            subnet_id:
            instance_type:
            instance_count:
            key_pair_name:
            security_group_ids:
            iam_instance_profile:
            new_tags:
            do_wait:
            return_only_ids:
            **kwargs:

        Returns:

        """
        # pylint: disable=no-member
        instances = self.ec2_resource.create_instances(
            ImageId=ami_id,
            BlockDeviceMappings=block_device_mappings,
            InstanceType=instance_type,
            NetworkInterfaces=[
                {
                    'SubnetId': subnet_id,
                    'DeviceIndex': 0,
                    'AssociatePublicIpAddress': False,
                    'Groups': security_group_ids
                }
            ],
            # SubnetId='subnet-afe05cc7',
            MinCount=1,
            MaxCount=instance_count,
            KeyName=key_pair_name,
            # SecurityGroupIds=security_group_ids,
            IamInstanceProfile=iam_instance_profile,
            TagSpecifications=[{'ResourceType': 'instance', 'Tags': new_tags}],
            **kwargs
        )

        created_instance_ids = []
        for instance in instances:
            created_instance_ids.append(instance.id)

        if do_wait:
            LOGGER.write('Waiting for instances to load...')
            waiter = self.ec2_client.get_waiter('instance_status_ok')
            waiter.wait(
                InstanceIds=created_instance_ids, WaiterConfig={'Delay': 30, 'MaxAttempts': 999})
            LOGGER.write('Instances loaded.')

        if return_only_ids:
            return created_instance_ids

        return instances

    def describe_instance_ids(self, filters: List[Dict[str, Union[str, List[str]]]] = None,
                              date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                              state: List[str] = None,
                              newest_only: bool = False) -> Union[List[str], str]:
        """

        Args:
            filters:
            date_range:
            state:
            newest_only:

        Returns:

        """
        # NOTE: Querying with empty Filters and / or InstanceIds returns all instances.
        filtered_instances = self.describe_instances(
            filters=filters, date_range=date_range, state=state, newest_only=newest_only)

        if isinstance(filtered_instances, list):
            if len(filtered_instances) > 0:
                return [_['InstanceId'] for _ in filtered_instances]

            return []

        return filtered_instances['InstanceId']

    # pylint: disable=too-many-arguments
    def describe_instance_dns_names(self, instance_ids: List[str] = None,
                                    filters: List[Dict[str, Union[str, List[str]]]] = None,
                                    date_range: Tuple[
                                        datetime.date, Optional[datetime.date]] = None,
                                    state: List[str] = None, get_private_dns_name: bool = True,
                                    newest_only: bool = True) -> Optional[List[str]]:
        """Gets the DNS names for instances based on a query.

        Args:
            instance_ids (List[str]): A set of instance Ids to use for the query.
            filters (List[Dict[str, Union[str, List[str]]]]): A set of filters to use for the
            query.
            date_range (Tuple[datetime.date, Optional[datetime.date]]): A date range to use for
            the query.  This is a tuple of datetime.date.  If there's only one date, set the 2nd
            value to None.
            state (List[str]): A list of possible instance states for the query.
            get_private_dns_name (bool): Whether or not to retrieve the private DNS value or
            public.  NOTE: For the managed ATS, only use private DNS.
            newest_only (bool): Whether or not to only return the newest out of all returned
            instances.

        Returns:
            Optional[Union[str, List[str]]]: Either a list of dns names, a dns name string or None.
        """
        filtered_instances = self.describe_instances(
            instance_ids=instance_ids, filters=filters, date_range=date_range, state=state,
            newest_only=newest_only)

        # If it's a list and not empty...
        if filtered_instances and isinstance(filtered_instances, list):
            if get_private_dns_name:
                return [_['PrivateDnsName'] for _ in filtered_instances]
            return [_['PublicDnsName'] for _ in filtered_instances]

        # If it's an empty list...
        if isinstance(filtered_instances, list):
            return None

        # If it's a dict (default for a single instance returned by the query)...
        if get_private_dns_name:
            return [filtered_instances['PrivateDnsName']]
        return [filtered_instances['PublicDnsName']]

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-branches
    def describe_instances(self, instance_ids: List[str] = None,
                           filters: List[Dict[str, Union[str, List[str]]]] = None,
                           date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                           state: List[str] = None,
                           newest_only: bool = True) -> Union[List[Dict], Dict]:
        """

        Args:
            filters:
            instance_ids:
            date_range:
            state:
            newest_only:

        Returns:

        """
        # NOTE: Querying with empty Filters and / or InstanceIds returns all instances.
        response = self.ec2_client.describe_instances(
            Filters=filters or [], InstanceIds=instance_ids or [])
        self._validate_response_status(response)

        if state is not None and len(state) > 0:
            state = [_.lower() for _ in state]

        filtered_instances = []
        # pylint: disable=too-many-nested-blocks
        for reservation in self._get_reservations_value(response):
            for instance in self._get_instances_value(reservation):
                if date_range is not None:
                    start_date, end_date = self._parse_date_range(date_range)
                    launch_date = self._get_launch_date_value(instance)
                    if launch_date >= start_date and end_date is not None:
                        if launch_date <= end_date:
                            if state is not None and len(state) > 0:
                                if self._get_state_name_value(instance).lower() in state:
                                    filtered_instances.append(instance)
                            else:
                                filtered_instances.append(instance)
                    elif launch_date >= start_date:
                        if state is not None and len(state) > 0:
                            if self._get_state_name_value(instance).lower() in state:
                                filtered_instances.append(instance)
                        else:
                            filtered_instances.append(instance)
                else:
                    if state is not None and len(state) > 0:
                        if self._get_state_name_value(instance).lower() in state:
                            filtered_instances.append(instance)
                    else:
                        filtered_instances.append(instance)

        if newest_only and len(filtered_instances) > 0:
            return self._get_newest_instance(filtered_instances)

        return filtered_instances

    # pylint: disable=too-many-arguments
    def get_instance_objects(self, instance_ids: List[str] = None,
                             filters: List[Dict[str, Union[str, List[str]]]] = None,
                             date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                             state: List[str] = None,
                             newest_only: bool = True) -> Union[List[Any], dict]:
        """

        Args:
            filters:
            instance_ids:
            date_range:
            state:
            newest_only:

        Returns:

        """
        _instance_ids = []
        if instance_ids is not None and len(instance_ids) > 0:
            _instance_ids = instance_ids
        elif filters is not None and len(filters) > 0:
            _instance_ids = self.describe_instance_ids(
                filters=filters, date_range=date_range, state=state, newest_only=newest_only)
        elif date_range is not None and isinstance(date_range, tuple):
            _instance_ids = self.describe_instance_ids(
                date_range=date_range, state=state, newest_only=newest_only)
        elif state is not None and len(state) > 0:
            _instance_ids = self.describe_instance_ids(state=state, newest_only=newest_only)
        else:
            raise TypeError('You must provide a valid list of instance ids.')

        # In the case where we only get a single instance Id back (instead of a list),
        # just return a single instance object.
        if isinstance(_instance_ids, str):
            if len(_instance_ids) > 0:
                # pylint: disable=no-member
                return self.ec2_resource.Instance(_instance_ids)

            return []

        instances = []
        for instance_id in _instance_ids:
            # pylint: disable=no-member
            instances.append(self.ec2_resource.Instance(instance_id))

        return instances

    def get_instances_with_expired_termination_date(self) -> List[str]:
        """Returns a list of instances whose TerminationDate tag value is <= today().

        If no matches are found, an empty list will be returned.

        Returns:
            List[str]: A list of instance Ids (or an empty list).
        """
        # Query for all instance having a TerminateDate value.
        instances_with_termination_date = self.describe_instance_ids(
            filters=[{'Name': 'tag-key', 'Values': ['TerminationDate']}],
            state=DEFAULT_QUERY_INSTANCE_STATES
        )

        # Of the instances with a TerminationDate, query for the value of their TerminationDate.
        tag_data = self.get_resource_tag_data(
            resource_ids=instances_with_termination_date,
            tag_keys=['TerminationDate']
        )

        # Of the instances with a TerminationDate, find those whose date is <= today's date.
        instances_to_terminate: List[str] = []
        for tag_value in tag_data['Tags']:
            if tag_value['Value']:
                termination_date = datetime.strptime(tag_value['Value'], '%Y-%m-%d').date()
                if termination_date <= datetime.today().date():
                    instances_to_terminate.append(tag_value['ResourceId'])

        if instances_to_terminate:
            LOGGER.write(f'Found {len(instances_to_terminate)} instances needing termination:'
                         f' {instances_to_terminate}')
        else:
            LOGGER.write('No instances were found in need of stopping or terminating.')
        return instances_to_terminate

    def get_resource_tag_data(self, resource_ids: List[str],
                              tag_keys: List[str]) -> Dict[str, Any]:
        """Gets the value of the specified tags for a specified list of instance Ids.

        Args:
            resource_ids (List[str]): A list of resource Ids to query.
            tag_keys (List[str]): A list of tag key names.

        Returns:
            Dict[str, Any]: A dict containing data pertaining to the
            values of tags, resource-ids, etc.  It has the following structure:
                {
                    'Tags': [
                        {
                            'Key': (str)'<KenName>',
                            'Value': (str)'<KeyValue>',
                            'ResourceId': (str)'<resource id>',
                            'ResourceType': (str)'<type of resource>'
                        }
                    ],
                    'ResponseMetadata': {
                        'RequestId': (str)'<request id>',
                        'HTTPStatusCode': (int)<status_code>
                        'HTTPHeaders': (dict: 4){<header dict>},
                        'RetryAttempts': (int)<retry count>
                    }
                }
        """
        return self.ec2_client.describe_tags(
            Filters=[
                {'Name': 'resource-id', 'Values': resource_ids},
                {'Name': 'tag-key', 'Values': tag_keys}
            ]
        )

    def reboot_instances(self, instance_ids: List[str] = None,
                         filters: List[Dict[str, Union[str, List[str]]]] = None,
                         date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                         do_wait: bool = True) -> None:
        """

        Args:
            filters:
            instance_ids:
            date_range:
            do_wait:

        Returns:

        """
        _instance_ids = []
        if instance_ids is not None and len(instance_ids) > 0:
            _instance_ids = instance_ids
        elif filters is not None and len(filters) > 0:
            _instance_ids = self.describe_instance_ids(
                filters=filters, date_range=date_range, state=['running'])
        else:
            raise TypeError('You must provide a valid list of instance ids.')

        dns_names = self.private_dns_names_to_public(
            self.describe_instance_dns_names(_instance_ids, newest_only=False)
        )
        LOGGER.write(f'Rebooting the following instances: {dns_names}')
        self.ec2_client.reboot_instances(InstanceIds=_instance_ids)

        if do_wait:
            LOGGER.write('Waiting for instances to reboot...')

            # Wait for a bit for the instance to start the reboot.  If you try to wait for the
            # socket before the instance has started rebooting, then the socket will be found
            # and the waiter will think the system's rebooted already.
            time.sleep(30)
            for dns_name in dns_names:
                LOGGER.write(f'Waiting for instance {dns_name} to reboot.')
                self.wait_for_socket_on_instance(dns_name=dns_name)
                LOGGER.write(f'Instance {dns_name} rebooted.')

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def send_commands(self, instance_ids: List[str] = None,
                      filters: List[Dict[str, Union[str, List[str]]]] = None,
                      date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                      state: List[str] = None, commands: List[str] = None,
                      do_wait: bool = True, retry_count: int = 60,
                      total_command_run_time: int = 600,
                      log_error_as_warning: bool = False,
                      return_standard_output: bool = False,
                      platform_type: str = 'Windows') -> Optional[str]:
        """

        Args:
            instance_ids:
            filters:
            date_range:
            state:
            commands:
            do_wait:
            retry_count:
            total_command_run_time:
            log_error_as_warning:
            return_standard_output:
            platform_type:

        Returns:

        """
        _instance_ids = []
        if instance_ids is not None and len(instance_ids) > 0:
            _instance_ids = instance_ids
        elif filters is not None and len(filters) > 0:
            _instance_ids = self.describe_instance_ids(
                filters=filters, date_range=date_range, state=state)
        else:
            raise TypeError('You must provide a valid list of instance ids.')

        if len(_instance_ids) == 0:
            LOGGER.write('No instances found to run commands on.')
            return None

        _document_name = ''
        if platform_type == 'Windows':
            _document_name = 'AWS-RunPowerShellScript'
        elif platform_type == 'Linux':
            _document_name = 'AWS-RunShellScript'

        # If there's a problem when trying to run a command (such as when the instance hasn't
        # properly been added to the AWS Session Manager, then try waiting and/or (on every 3rd
        # try) rebooting the instance.
        response: Dict[str, Any] = {}
        for try_number in range(retry_count):
            try:
                response = self.ssm_client.send_command(
                    InstanceIds=_instance_ids,
                    DocumentName=_document_name,
                    Parameters={
                        'commands': commands
                    }
                )
                break
            except ClientError as ex:
                LOGGER.write(ex, 'exception')
                raise
            except Exception as ex:  # pylint: disable=broad-except
                if try_number < retry_count - 1:
                    LOGGER.write('An error occurred while sending a command.  Retry # '
                                 '{}'.format(try_number))

                    if try_number % 3 == 0:
                        LOGGER.write('Rebooting instances before retrying.')
                        self.reboot_instances(instance_ids=instance_ids)

                    LOGGER.write('Waiting for a bit before the retry...')
                    time.sleep(60)
                else:
                    LOGGER.write('The following exception was raised when running the command: '
                                 '{}'.format(str(ex)), 'exception')
                    raise ex

        if not do_wait:
            LOGGER.write('Not waiting for command invocation to complete.')
            return None

        # Wait a little bit for the invocation to resolve.
        time.sleep(3)

        # Poll the status of the commands until they're completed on all instances.
        # If there's a non-pass result on an instance, then update the step to reflect it.
        # TODO: In the case of multiple instances, this needs to be updated to append to
        # the data section as well as keep status priority (don't overwrite a failed with
        #  a passed).
        command_id = response['Command']['CommandId']
        all_done = False
        instance_command_statuses = [{'Id': _, 'Completed': False} for _ in _instance_ids]
        wait_start_time = time.time()
        while not all_done:
            if time.time() - wait_start_time > total_command_run_time:
                LOGGER.write('Total command run time exceeded!', 'error')
                raise TimeoutError('Total command run time exceeded!')

            all_done = True
            for instance_command_status in instance_command_statuses:
                if instance_command_status['Completed']:
                    continue

                output = self.ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=instance_command_status['Id']
                )
                LOGGER.write(
                    f'Instance {instance_command_status["Id"]} Status: {output["Status"]}  '
                    f'Command Run Time: {timedelta(seconds=time.time() - wait_start_time)}'
                )

                if output['StandardOutputContent'] != '':
                    LOGGER.write(
                        'StandardOutputContent: {}'.format(output['StandardOutputContent']))
                    if return_standard_output:
                        return output['StandardOutputContent'].strip()

                if output['StandardErrorContent'] != '':
                    # In the case of an error being needed to trigger a response, such as trying
                    # to add feeds that are already added, you can tell this method to treat
                    # that error as just a warning and to set the step to passed with the
                    # StandardErrorContent attached.  This is used in the main() function.
                    if not log_error_as_warning:
                        LOGGER.write('StandardErrorContent: {}'.format(
                            output['StandardErrorContent']), 'error')
                    else:
                        LOGGER.write('Warning from StandardErrorContent: {}'.format(
                            output['StandardErrorContent']))

                    # Go ahead and return from here as we don't want to progress any further.
                    # TODO: This will *also* need to be updated for multiple masters.
                    return output['StandardErrorContent']

                if output['Status'] == 'TimedOut':
                    LOGGER.write('One or more commands timed out on instance {}.  Commands: {}'
                                 .format(instance_command_status['Id'], commands), 'error')
                    instance_command_status['Completed'] = True

                if output['Status'] == 'Failed':
                    LOGGER.write(
                        'One or more commands failed on instance {}.  Commands: {}'.format(
                            instance_command_status['Id'], commands), 'error')
                    instance_command_status['Completed'] = True

                if output['Status'] == 'InProgress':
                    all_done = False

                if output['Status'] == 'Success':
                    instance_command_status['Completed'] = True

            if not all_done:
                time.sleep(5)

    def create_or_update_tag_value(self, resource_ids: List[str],
                                   tags: List[Dict[str, str]]) -> None:
        """Creates or updates the value of a tag for one or more resources.

        Args:
            resource_ids (List[str]): A list of resource Id strings.
            tags (List[Dict[str, str]]): A list of dicts representing the tag and value to set.
            It has the following structure:
                [{'Key': '<tag_name>', 'Value': <tag_value>}]

        Returns:
            None: None
        """
        response = self.ec2_client.create_tags(
            Resources=resource_ids,
            Tags=tags
        )
        self._validate_response_status(response)

    def wait_for_instance_state(self, instance_ids: List[str] = None,
                                filters: List[Dict[str, Union[str, List[str]]]] = None,
                                date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                                state: List[str] = None) -> None:
        """

        Args:
            filters:
            date_range:
            instance_ids:
            state:

        Returns:

        """
        _instance_ids = []
        if instance_ids is not None and len(instance_ids) > 0:
            _instance_ids = instance_ids
        elif filters is not None and len(filters) > 0:
            _instance_ids = self.describe_instance_ids(filters=filters, date_range=date_range)
        else:
            raise TypeError('You must provide a valid list of instance ids.')

        waiting = True
        while waiting:
            waiting = False
            status_object = self.ec2_client.describe_instance_status(
                InstanceIds=_instance_ids or []
            )
            for instance in status_object['InstanceStatuses']:
                if instance['InstanceState']['Name'] not in (state or ['running']):
                    waiting = True
                    break

            if waiting:
                time.sleep(10)

    def public_dns_names_to_ids(self, instance_dns_names: List[str]) -> List[str]:
        """Takes in a list of instance public DNS names and returns a list of instance Id strings.

        Args:
            instance_dns_names (List[str]): A list of public DNS names to query.

        Returns:
            List[str]: A list of instance Id strings.
        """
        return self.describe_instance_ids(
            filters=[
                {
                    'Name': 'private-dns-name',
                    'Values': self.public_dns_names_to_private(instance_dns_names)
                }
            ]
        )
