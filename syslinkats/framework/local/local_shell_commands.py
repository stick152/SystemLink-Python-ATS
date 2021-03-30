"""
local_shell_commands.py
"""
import subprocess
import sys
from typing import Dict

from syslinkats.framework.logging.auto_indent import AutoIndent

LOGGER = AutoIndent(sys.stdout)


def call_subprocess_popen(command_to_run: str = None, timeout_sec: int = 3600) -> Dict[str, str]:
    """Calls subprocess.Popen and returns the process.

    Args:
        command_to_run (str): The command to run in Popen.
        timeout_sec (int): Timeout in seconds.

    Returns:
        Dict[str, str]: A named tuple containing return_code, stdout, and stderr.

    Raises:
        Various exceptions.
    """
    if not command_to_run:
        command_to_run = ''

    try:
        LOGGER.write('command: ' + command_to_run)
        process = subprocess.Popen(
            command_to_run,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            start_new_session=True)
        outs, errs = process.communicate(timeout=timeout_sec)
    except subprocess.CalledProcessError as cpe:
        LOGGER.write(
            '{0}\n{1}\n{2}'.format(cpe.cmd, cpe.output, cpe.returncode), 'error')
        raise
    except subprocess.TimeoutExpired as t_e:
        LOGGER.write('{0}\n{1}\n{2}'.format(t_e.cmd, t_e.output, t_e.timeout), 'error')
        raise
    except Exception as g_e:
        LOGGER.write(str(g_e), 'error')
        raise
    else:
        LOGGER.write('''[-] command result: return_code: {0} stdout: {1} stderr: {2} '''.format(
            process.returncode, outs, errs))

        return {'return_code': process.returncode, 'stdout': outs, 'stderr': errs}
