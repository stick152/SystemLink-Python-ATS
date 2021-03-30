#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
image_wrapper.py
"""
import datetime
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.aws import AWSBase

# Set up AutoIndent for logging.
LOGGER = AutoIndent(stream=sys.stdout)


class AWSImage(AWSBase):
    """"""

    def __init__(self, **kwargs):
        """Initialize an instance of the class."""
        super().__init__(**kwargs)

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
        pass

    @staticmethod
    def _get_creation_date_value(image: dict = None) -> datetime.date:
        """

        Args:
            image:

        Returns:

        """
        if image is not None and isinstance(image, dict):
            return AWSImage._get_creation_time_value(image).date()
        else:
            raise TypeError('The provided image must be a valid image dict.')

    @staticmethod
    def _get_creation_time_value(image: dict = None) -> datetime.datetime:
        """

        Args:
            image:

        Returns:

        """
        if image is not None and isinstance(image, dict) and 'CreationDate' in image:
            return datetime.datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            raise TypeError('The provided image must be a valid image dict.')

    @staticmethod
    def _get_image_days_age(image: dict = None) -> int:
        """

        Args:
            image:

        Returns:

        """
        if image is not None and isinstance(image, dict):
            return (datetime.datetime.utcnow().date() -
                    AWSImage._get_creation_date_value(image)).days
        else:
            raise TypeError('The provided image must be a valid image dict.')

    @staticmethod
    def _get_newest_image(images: List[dict] = None) -> dict:
        """

        Args:
            images:

        Returns:

        """
        if images is not None and len(images) > 0:
            newest_image = None
            now = datetime.datetime.utcnow()
            for image in images:
                creation_datetime = AWSImage._get_creation_time_value(image)
                if newest_image is None:
                    newest_image = image
                else:
                    if (now - creation_datetime) \
                            < (now - AWSImage._get_creation_time_value(newest_image)):
                        newest_image = image
            return newest_image
        else:
            raise TypeError('The provided image must be a valid image dict.')

    @staticmethod
    def _get_state_value(image: dict = None) -> str:
        """

        Args:
            image:

        Returns:

        """
        if image is not None and isinstance(image, dict) and 'State' in image:
            return image['State']
        else:
            raise TypeError('The provided image must be a valid image dict.')

    def _create_image_from_data_object(self, image_data: Dict[str, str] = None,
                                       **kwargs) -> Optional[str]:
        """

        Args:
            image_data:
            **kwargs:

        Returns:

        """
        if image_data is not None and isinstance(image_data, dict):
            if 'InstanceId' not in image_data:
                return None
            else:
                if 'Name' in image_data:
                    name = image_data['Name']
                else:
                    name = 'auto-gen-' + image_data['InstanceId']

                if 'Description' in image_data:
                    description = image_data['Description']
                else:
                    description = ''

                if 'Tags' in image_data:
                    image_tags = image_data['Tags']
                else:
                    image_tags = []

                created_image_id = self.ec2_client.create_image(
                    InstanceId=image_data['InstanceId'],
                    Name=name,
                    Description=description,
                    **kwargs)

                if len(image_tags) > 0:
                    image_object = self.ec2_resource.Image(created_image_id)
                    image_object.create_tags(Tags=image_tags)

                return created_image_id
        else:
            raise TypeError('You must provide a valid image data object.')

    def _create_image_from_instance_id(self, instance_id: str = None,
                                       **kwargs) -> Optional[str]:
        """

        Args:
            instance_id:
            **kwargs:

        Returns:

        """
        if instance_id is not None and isinstance(instance_id, str):
            created_image_id = self.ec2_client.create_image(
                InstanceId=instance_id,
                Name='auto-gen-' + instance_id,
                Description='',
                **kwargs)
            return created_image_id
        else:
            raise TypeError('You must provide a valid instance id.')

    def cleanup_images(self, image_ids: List[str] = None,
                       filters: List[Dict[str, Union[str, List[str]]]] = None,
                       date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                       owners: List[str] = None, state: List[str] = None) -> None:
        """

        Args:
            image_ids:
            filters:
            date_range:
            owners:
            state:

        Returns:

        """
        image_objects = self.get_image_objects(
            image_ids=image_ids, filters=filters, date_range=date_range, state=state,
            owners=owners, newest_only=False)

        if len(image_objects) == 0:
            LOGGER.write('No matching image objects were found for cleanup.')
            return

        _image_ids = []
        for image_object in image_objects:
            LOGGER.write('Image {} will be de-registered.'.format(image_object.image_id))
            _image_ids.append(image_object.image_id)
            image_object.deregister()

    def create_images(self, instance_ids: List[str], image_data: List[Dict[str, str]] = None,
                      do_wait: bool = True, **kwargs) -> List[str]:
        """

        Args:
            instance_ids:
            image_data:
            do_wait:
            **kwargs:

        Returns:

        """
        created_image_ids = []
        if image_data is not None and len(image_data) > 0:
            for data in image_data:
                created_image_id = self._create_image_from_data_object(image_data=data, **kwargs)
                if created_image_id:
                    created_image_ids.append(created_image_id)
        elif instance_ids is not None and len(instance_ids) > 0:
            for instance_id in instance_ids:
                created_image_id = self._create_image_from_instance_id(
                    instance_id=instance_id, **kwargs)
                created_image_ids.append(created_image_id)
        else:
            raise TypeError(
                'You must provide either a list of instance Ids or instance data object.')

        if do_wait:
            if do_wait:
                LOGGER.write('Waiting for images to become available.')
                waiter = self.ec2_client.get_waiter('image_available')
                waiter.wait(ImageIds=created_image_ids)
                LOGGER.write('Images available.')

        return created_image_ids

    def describe_image_ids(self, filters: List[Dict[str, Union[str, List[str]]]] = None,
                           date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                           owners: List[str] = None, state: List[str] = None,
                           newest_only: bool = True) -> Union[List[str], str, None]:
        """
        NOTE: Querying with empty Filters or Owners returns all instances.

        Args:
            filters:
            date_range:
            owners:
            state:
            newest_only:

        Returns:

        """
        filtered_images = self.describe_images(
            filters=filters, date_range=date_range, owners=owners, state=state,
            newest_only=newest_only)

        if isinstance(filtered_images, list):
            return [_['ImageId'] for _ in filtered_images]
        elif isinstance(filtered_images, dict):
            return filtered_images['ImageId']
        else:
            return filtered_images

    def describe_image_tags(self, image_id: str = None,
                            filters: List[Dict[str, Union[str, List[str]]]] = None,
                            date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                            owners: List[str] = None,
                            state: List[str] = None,) -> Optional[List[Dict[str, str]]]:
        """
        NOTE: Querying with empty ImageIds, Filters or Owners returns all images.

        Args:
            image_id:
            filters:
            date_range:
            owners:
            state:

        Returns:
            Tags list of dicts for a single image.
        """
        filtered_image = self.describe_images(
            image_ids=[image_id], filters=filters, date_range=date_range, owners=owners,
            state=state, newest_only=True)

        if filtered_image is not None:
            if 'Tags' in filtered_image:
                return filtered_image['Tags']
            else:
                return []
        else:
            return filtered_image

    def describe_images(self, image_ids: List[str] = None,
                        filters: List[Dict[str, Union[str, List[str]]]] = None,
                        date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                        owners: List[str] = None, state: List[str] = None,
                        newest_only: bool = True) -> Union[List[Dict], Dict, None]:
        """
        NOTE: Querying with empty Filters, InstanceIds or Owners returns all instances.

        Args:
            image_ids:
            filters:
            date_range:
            owners:
            state:
            newest_only:

        Returns:

        """
        response = self.ec2_client.describe_images(
            Filters=filters or [], ImageIds=image_ids or [], Owners=owners or [])
        self._validate_response_status(response)

        filtered_images = []
        for image in response['Images']:
            if date_range is not None:
                start_date, end_date = self._parse_date_range(date_range)
                creation_date = self._get_creation_date_value(image)
                if creation_date >= start_date and end_date is not None:
                    if creation_date <= end_date:
                        if state is not None and len(state) > 0:
                            if self._get_state_value(image).lower() in state:
                                filtered_images.append(image)
                        else:
                            filtered_images.append(image)

                elif creation_date >= start_date:
                    if state is not None and len(state) > 0:
                        if self._get_state_value(image).lower() in state:
                            filtered_images.append(image)
                    else:
                        filtered_images.append(image)
            else:
                if state is not None and len(state) > 0:
                    if self._get_state_value(image).lower() in state:
                        filtered_images.append(image)
                else:
                    filtered_images.append(image)

        if newest_only:
            if len(filtered_images) > 0:
                return self._get_newest_image(filtered_images)
            else:
                return None
        else:
            return filtered_images

    def get_image_objects(self, image_ids: List[str] = None,
                          filters: List[Dict[str, Union[str, List[str]]]] = None,
                          date_range: Tuple[datetime.date, Optional[datetime.date]] = None,
                          state: List[str] = None, owners: List[str] = None,
                          newest_only: bool = True) -> List[Any]:
        """

        Args:
            image_ids:
            filters:
            date_range:
            state:
            owners:
            newest_only:

        Returns:

        """
        _image_ids = []
        if image_ids is not None and len(image_ids) > 0:
            _image_ids = image_ids
        elif filters is not None and len(filters) > 0:
            _image_ids = self.describe_image_ids(
                filters=filters, date_range=date_range, owners=owners, newest_only=newest_only)
        elif date_range is not None and isinstance(date_range, tuple):
            _image_ids = self.describe_image_ids(
                date_range=date_range, owners=owners, newest_only=newest_only)
        elif state is not None and len(state) > 0:
            _image_ids = self.describe_image_ids(
                state=state, owners=owners, newest_only=newest_only)
        else:
            raise TypeError('You must provide a valid list of instance ids.')

        if isinstance(_image_ids, str):
            return self.ec2_resource.Image(_image_ids)

        image_objects = []
        for image_id in _image_ids:
            image_objects.append(self.ec2_resource.Image(image_id))

        return image_objects


# if __name__ == '__main__':
    # Examples...
    # aws_image = AWSImage(region_name='us-east-2')
    # my_filters = [
    #     {
    #         'Name': 'name',
    #         'Values': ['MinionBase_09-Aug-2018']
    #     }]
    # date = datetime.datetime.strptime('01082018', '%d%m%Y').date()
    #
    # my_image_ids = []
    # my_instance_ids = ['i-0f66cfa1f5ff8170f']
    # my_image_data = [
    #     {
    #         'InstanceId': 'i-0f66cfa1f5ff8170f',
    #         'Name': 'Example_01',
    #         'Description': 'Some description.',
    #         'Tags': [
    #             {
    #                 'Key': 'maj_min_build',
    #                 'Value': '18.5.0'
    #             },
    #             {
    #                 'Key': 'Feeds',
    #                 'Value': 'ni-systemlink-server ni-systemlink-opc-module '
    #                          'ni-systemlink-test-module ni-systemlink-jupyterhub-module'
    #             }
    #         ]
    #     }
    # ]

    # EXAMPLE: Create images.
    # created_image_ids = aws_image.create_images(
    #     instance_ids=my_instance_ids, image_data=my_image_data)
    # print(created_image_ids)

    # EXAMPLE: Cleanup images based on list of Ids.
    # aws_image.cleanup_images(image_ids=my_image_ids)
    # print('done')

    # EXAMPLE: Get data about one or more AMIs based on a query.
    # response = aws_image.describe_images(
    #     filters=my_filters,
    #     date_range=(date, datetime.date.today()), owners=['self'],
    #     state=['available'],
    #     newest_only=True)
    # if type(response) is list:
    #     for r in response:
    #         print(r)
    # elif type(response) is dict:
    #     print(response)
    # else:
    #     print('Image data was not found.')

    # EXAMPLE: Get one or more image objects based on a query.
    # response = aws_image.get_image_objects(
    #     # image_ids=['ami-6f14270a', 'ami-0eefa79d1efec3915'],
    #     # filters=my_filters,
    #     date_range=(date, datetime.date.today()),
    #     state=['available'],
    #     owners=['self'],
    #     newest_only=False
    # )
    # if type(response) is list:
    #     for r in response:
    #         print(r)
    # elif type(response) is dict:
    #     print(response)
    # else:
    #     print('An image object was not found.')
