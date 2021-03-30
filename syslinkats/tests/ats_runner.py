import argparse
import os
import sys
from os.path import expanduser

import pytest

from syslinkats import ats_config_file
from syslinkats.framework.common.argparse_helpers import bool_from_str, int_from_str


def parse_arguments():
    """Returns options to the caller.

    This function parses out and returns arguments and options from the
    commandline arguments.

    """
    parser = argparse.ArgumentParser(description='Run tests against the '
                                                 'nismsws web service.')
    parser.add_argument(
        '--junit-xml-path', action='store', type=str,
        default=os.path.join(expanduser('~'), 'result.xml'),
        dest='junit_xml_path',
        help='The path to the file that pytest stores its results in.'
    )
    parser.add_argument(
        '--stop-on-first-failure', action='store', type=bool_from_str, default=False,
        dest='stop_on_first_failure',
        help='''When True, this option will cause pytest to stop immediately upon the first 
        encountered test failure.'''
    )
    parser.add_argument(
        '--use-dev-worker', action='store', type=bool_from_str, default=False,
        dest='use_dev_worker',
        help='''Tells the runners that you want to test using the syslink_worker_name
        specified in default_conf.json instead of the auto-detected AWS ATS instance(s).''',
    )
    parser.add_argument(
        '--ats-config-path', action='store', type=str, default=ats_config_file(),
        dest='ats_config_path',
        help='''The path to the JSON file with the configuration for the dev master.''',
    )
    parser.add_argument(
        '--cpu-count', action='store', type=int_from_str, default=0,
        dest='cpu_count',
        help='The number of CPUs to run tests on.'
    )
    parser.add_argument(
        '--mark-string', action='store', type=str, default='daily and not long_run_time',
        dest='mark_string',
        help='A bool string of marks (i.e.: "all_buckets and daily not long_running")'
    )
    parser.add_argument(
        '--disable-reporting', action='store', type=bool_from_str, default=True,
        dest='disable_reporting',
        help='Disables Test Monitor reporting for the test run.'
    )
    parser.add_argument(
        '--operator', action='store', type=str, default='NI Test',
        dest='operator',
        help='The Jenkins user who started the test run.'
    )

    args, unknown = parser.parse_known_intermixed_args()
    print(f'args: {args}  unknown: {unknown}')

    return args, unknown


def main():
    args, pass_through_args = parse_arguments()
    cmd_args = [
        '-n' if args.cpu_count else '',
        str(args.cpu_count) if args.cpu_count else '',
        '-x' if args.stop_on_first_failure is True else '',
        '-m', args.mark_string,
        '--junitxml', args.junit_xml_path,
        '--use-dev-worker', str(args.use_dev_worker),
        '--ats-config-path', args.ats_config_path,
        '--disable-reporting', str(args.disable_reporting),
        '--operator', str(args.operator),
        '--pass-through-args', str(pass_through_args),
        # region Ignores for bucket conversion.
        '--ignore', 'common/',
        '--ignore', 'buckets/nxg',
        # endregion
    ]

    exit_code = pytest.main(cmd_args)
    return exit_code

    # TODO: Run this a second time when/if we have tests that are marked as not supporting the
    #  -n arg.
    # TODO: Will also need to figure out what to do about reports in that case.


if __name__ == '__main__':
    _exit_code = main()
    sys.exit(_exit_code)
