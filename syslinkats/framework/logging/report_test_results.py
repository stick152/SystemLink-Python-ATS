import argparse
import ast
import ntpath
import xml.etree.ElementTree

from botocore.exceptions import ClientError

from syslinkats.data.common.aws_default_parameters import DEFAULT_AWS_SYSLINK_ACCESS_DATA
from syslinkats.tests.buckets.file.utils.file_web_api import FileWebApi
from syslinkats.tests.buckets.testmon.utils import testmon_constants
from syslinkats.tests.buckets.testmon.utils.testmon_util import TestMonitorUtil
from syslinkats.tests.buckets.testmon.utils.testmon_web_api import TestMonitorWebApi
from syslinkats.tests.common.utils.testing_helper import NoWorkerFoundError
from syslinkats.tests.pytest_reporting.pytest_reporting import query_test_instance_installation_tags

file_web_api = None
test_monitor_util = None
suite_name = None
classes = {}
steps = {}


def traverse_xml_tree(result_id=None, parent_id=None, node=None, depth=0):
    """

    Args:
        result_id:
        parent_id:
        node:
        depth:

    Returns:

    """
    if node is None:
        return
    if node.tag != 'testsuite' and node.tag != 'testcase':
        return

    if node.tag == 'testsuite':
        name = suite_name if suite_name else node.get('name')
    else:
        name = node.get('name')

    message = None
    error_or_failure_type = None
    stdout = None
    stderr = None
    if node.findall('error'):
        status = test_monitor_util.create_status_object(
            testmon_constants.ERRORED, 'Errored'
        )
        for child in node:
            if child.tag == 'error':
                error_or_failure_type = child.get('type')
                stdout = child.get('message')
                stderr = child.text

    elif node.findall('failure'):
        status = test_monitor_util.create_status_object(
            testmon_constants.FAILED, 'Failed'
        )
        for child in node:
            if child.tag == 'failure':
                error_or_failure_type = child.get('type')
                stdout = child.get('message')
                stderr = child.text
    elif node.findall('skipped'):
        status = test_monitor_util.create_status_object(
            testmon_constants.SKIPPED, 'Skipped'
        )
        for child in node:
            if child.tag == 'skipped':
                error_or_failure_type = child.get('type')
                stdout = child.get('message')
                stderr = child.text
    else:
        status = test_monitor_util.create_status_object(
            testmon_constants.PASSED, 'Passed'
        )

    class_name = node.get('classname')
    if class_name is not None:
        if class_name in classes:
            step = steps[classes[class_name]]
            parent_id = step['stepId']
        else:
            step = test_monitor_util.create_test_step(
                name=class_name.split('.')[-1],
                step_type='testbucket',
                parent_id=parent_id,
                result_id=result_id,
                status_type=status['statusType'],
                status_name=status['statusName'],
                total_time_in_seconds=0
            )
            classes[class_name] = step['stepId']
            steps[step['stepId']] = step
            parent_id = step['stepId']

    step_type = node.tag
    time = node.get('time')
    total_time_in_seconds = 0
    if time:
        total_time_in_seconds = float(time)

    step = test_monitor_util.create_test_step(
        name=name,
        step_type=step_type,
        parent_id=parent_id,
        result_id=result_id,
        status_type=status['statusType'],
        status_name=status['statusName'],
        total_time_in_seconds=total_time_in_seconds,
        data_model='Software',
        data=test_monitor_util.create_data_object(
            text=message,
            parameters=[{
                'stdout': stdout,
                'stderr': stderr,
                'Type': error_or_failure_type
            }])
    )
    steps[step['stepId']] = step
    test_monitor_util.update_all_parents(
        step_id=step['stepId'],
        status=status,
        total_time_in_seconds=total_time_in_seconds
    )

    for child in node:
        traverse_xml_tree(
            result_id=result_id,
            parent_id=step['stepId'],
            node=child,
            depth=depth + 1
        )


def parse_args():
    """Returns options to the caller.

        This function parses out and returns arguments and options from the
        commandline arguments.

    """
    parser = argparse.ArgumentParser(
        description='Parse a junit xml file and use it to create test steps '
                    'for a result.'
    )
    parser.add_argument(
        'file_path',
        help='The path to the junit xml file to parse.'
    )
    parser.add_argument(
        'suite_name',
        help='The name of the test suite.'
    )
    parser.add_argument(
        '-s', '--test_monitor_server_data',
        help='''A dict string with the following structure:
        "{
            'name': '<name>',
            'username': '<user name>',
            'password': '<password>'
        }"
        '''
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    # If the user omitted the test_monitor_server_data arg or passed in an empty string
    # (Jenkins does this), then use the default dict.  Otherwise, eval the string to a dict.
    if args.test_monitor_server_data is None or args.test_monitor_server_data == '':
        args.test_monitor_server_data = DEFAULT_AWS_SYSLINK_ACCESS_DATA
    else:
        args.test_monitor_server_data = ast.literal_eval(args.test_monitor_server_data)

    # Assign arguments to our globals.
    file_path = args.file_path
    suite_name = args.suite_name
    file_web_api = FileWebApi(
        worker_name=args.test_monitor_server_data['name'],
        username=args.test_monitor_server_data['username'],
        password=args.test_monitor_server_data['password']
    )
    test_monitor_util = TestMonitorUtil(
        TestMonitorWebApi(
            worker_name=args.test_monitor_server_data['name'],
            username=args.test_monitor_server_data['username'],
            password=args.test_monitor_server_data['password']
        )
    )

    try:
        installation_tags = query_test_instance_installation_tags()
    except (NoWorkerFoundError, ClientError):
        installation_tags = {}

    # Pull our result Id from file.
    top_result_id, is_top_level = test_monitor_util.get_result_id(
        serial_number=installation_tags.get('suite_version', None)
    )

    # Read the xml file contents
    with open(file_path, 'r') as nose_xml_file:
        file_contents = nose_xml_file.read()
    file_name = ntpath.basename(file_path)

    # Upload the xml file
    upload_response = file_web_api.upload_file(
        file_name=file_name, file_contents=file_contents
    )
    test_monitor_util.validate_expected_response(
        response_object=upload_response, expected_response=201
    )

    upload_response_json = upload_response.json()
    uploaded_file_id = upload_response_json['uri'].split('/')[-1]

    # Update the test result to include the attached file
    update_results_response = test_monitor_util.test_monitor_api.update_result(
        top_result_id,
        file_ids=[uploaded_file_id],
        replace=False,
        determine_status_from_steps=False
    )
    test_monitor_util.validate_expected_response(
        response_object=update_results_response, expected_response=200
    )

    # Load the xml file using the xml tree library
    e = None
    try:
        e = xml.etree.ElementTree.parse(file_path)
    except xml.etree.ElementTree.ParseError:
        exit(1)

    root = e.getroot()
    if root.tag == 'testsuites':
        for child in root:
            traverse_xml_tree(top_result_id, '', child, 0)
    else:
        traverse_xml_tree(top_result_id, '', root, 0)
